import importlib.resources
from enum import Enum, auto
from functools import lru_cache
from itertools import combinations
from math import factorial

import numpy as np

from .tensor import Tensor
from .tensor_operator import TensorOperator
from .character_table import CharacterTable
from . import projectors as projectors_package
from .log_formats import colorized_logger
logger = colorized_logger(__name__)


class DecompositionSummary(Enum):
    """
    Used to select a method of summarization of the results of the transform.
    """
    COMPONENTS = auto()
    NORMS = auto()
    CONTENT = auto()
    SEQUENTIAL_CONTENT = auto()
    MEAN_CONTENT = auto()
    VARIANCE_CONTENT = auto()


class SchurTransform:
    """
    The main computation orchestration object.
    """
    max_dimension = 3
    max_degree = 6

    def transform(self,
        samples,
        summary: str='COMPONENTS',
        number_of_factors: int=None,
        character_table_filename: str=None,
        conjugacy_classes_table_filename: str=None,
    ):
        """
        :param samples: "Registered" spatial samples data. A multi-dimensional array, or
            nested list of lists of lists. The axis indices are respectively:

            - the index indicating the series/variable
            - the sample index
            - the spatial coordinate index

            If a dictionary, the keys may be case identifiers and each value must be a
            list of lists of lists (or numpy array) as above.
        :type samples: multi-dimensional array-like, or dict

        :param summary: Indication of what to return. Must be the string name of one of
            the members of the enum class :py:class:`DecompositionSummary`. See the
            cases for return value.
        :type summary: str

        :param number_of_factors: In case of one of the ``...CONTENT`` summary types,
            this integer provides the number of factors (number of variables) used in
            the joint moment. Currently this must be less than or equal to 6, unless you
            provide your own character table and conjugacy class information.
        :type number_of_factors: int

        :param character_table_filename: Only provide this argument if you wish to
            supply a character table for a symmetric group of degree higher than 6
            (beyond S6). Use the file format exemplified by ``s2.csv``, ``s3.csv``, etc.
            under the :py:mod:`schurtransform.character_tables` subpackage.
        :type character_table_filename: str

        :param conjugacy_classes_table_filename: Only provide this argument if you wish
            to supply a character table for a symmetric group of degree higher than 6
            (beyond S6). Use the file format exemplified by
            ``symmetric_group_conjugacy_classes.csv`` in the
            :py:mod:`schurtransform.character_tables` subpackage.
        :type conjugacy_classes_filename: str

        :return: Depending on the value of ``summary``,

            - ``COMPONENTS``. Returns the tensor components of the Schur-Weyl
              decomposition of the joint moment tensor, the tensor product over the
              series index.
            - ``NORMS``. Returns the Euclidean norms of the tensor components of the
              Schur-Weyl decomposition.
            - ``CONTENT``. Returns a list of distributions, one for each tensor
              component type, consisting of the Euclidean norms of that component of the
              decomposition of all N-factor joint moments, where N is the given
              ``number_of_factors``.
            - ``SEQUENTIAL_CONTENT``. Returns a list of distributions just as in the
              ``CONTENT`` case, except that only consecutive N-fold products are
              considered.
            - ``MEAN_CONTENT``. The means of the distributions obtained in the
              ``CONTENT`` case are provided (one for each tensor component type).
            - ``VARIANCE_CONTENT``. The variances of the distributions obtained in the
              ``CONTENT`` case are provided.

        :rtype: dict
        """
        if isinstance(samples, dict):
            return {case : self.transform(
                samples[case],
                summary = summary,
                number_of_factors = number_of_factors,
                character_table_filename = character_table_filename,
                conjugacy_classes_table_filename = conjugacy_classes_table_filename,
            ) for case in samples}

        if isinstance(samples, list):
            samples = np.array(samples)

        if len(samples.shape) != 3:
            logger.error(
                ''.join([
                    'Expected 3 axes:',
                    'series (random variable), sample, and spatial coordinate.',
                    'Got axes of sizes: %s',
                ]),
                samples.shape,
            )
            return

        number_of_series = samples.shape[0]
        dimension = samples.shape[2]
        summary = DecompositionSummary[summary]
        if summary in [DecompositionSummary.COMPONENTS, DecompositionSummary.NORMS]:
            degree = number_of_series
        else:
            degree = number_of_factors
            if number_of_factors is None:
                logger.error(
                    'For summary=%s you must supply a number of tensor factors.',
                    summary.name,
                )
                return

        logger.debug(
            'Calculating projectors of type degree=%s and dimension=%s.',
            degree,
            dimension,
        )
        projectors = self.recalculate_projectors(
            dimension=dimension,
            degree=degree,
        )
        if summary in [DecompositionSummary.COMPONENTS, DecompositionSummary.NORMS]:
            logger.debug('Centralizing input sample data.')
            centered = self.recenter_at_mean(samples)
            logger.debug('Creating covariance tensor.')
            covariance_tensor = self.calculate_covariance_tensor(centered)
            logger.debug('Decomposing covariance tensor.')
            decomposition = self.calculate_decomposition(covariance_tensor, projectors)
            logger.debug('Validating decomposition.')
            self.validate_decomposition(decomposition, covariance_tensor)

            if summary == DecompositionSummary.COMPONENTS:
                return decomposition

            if summary == DecompositionSummary.NORMS:
                return {i: np.linalg.norm(component.data) for i, component in decomposition.items()}

        if summary in [
            DecompositionSummary.CONTENT,
            DecompositionSummary.SEQUENTIAL_CONTENT,
            DecompositionSummary.MEAN_CONTENT,
            DecompositionSummary.VARIANCE_CONTENT,
        ]:
            if summary == DecompositionSummary.SEQUENTIAL_CONTENT:
                index_combinations = [
                    [i + j for j in range(degree)] for i in range(number_of_series-(degree-1))
                ]
            else:
                index_combinations = combinations(list(range(number_of_series)), degree)

            character_table = CharacterTable(degree=degree)
            content = {key : [] for key in character_table.get_characters()}
            for combination in index_combinations:
                subsample = samples[list(combination), :, :]
                centered = self.recenter_at_mean(subsample)
                covariance_tensor = self.calculate_covariance_tensor(centered)
                decomposition = self.calculate_decomposition(covariance_tensor, projectors)
                self.validate_decomposition(decomposition, covariance_tensor)
                norms = {i: np.linalg.norm(comp.data) for i, comp in decomposition.items()}
                for i, norm in norms.items():
                    content[i].append(norm)

            if summary is DecompositionSummary.CONTENT:
                return content
            if summary is DecompositionSummary.SEQUENTIAL_CONTENT:
                return content
            if summary is DecompositionSummary.MEAN_CONTENT:
                return {i : np.mean(content[i]) for i in content.keys()}
            if summary is DecompositionSummary.VARIANCE_CONTENT:
                return {i : np.var(content[i]) for i in content.keys()}

    @lru_cache(maxsize=5)
    def recalculate_projectors(self,
        dimension: int=None,
        degree: int=None,
        get_cached: bool=True,
    ):
        """
        (This function is wrapped by ``functools.lru_cache``).

        :param dimension: The dimension of the base vector space.
        :type dimension: int

        :param degree: The number of factors in the tensor product.
        :type degree: int

        :param get_cached: Default True. If True, attempts to retrieve the projectors
            from cached numpy-exported archive files.
        :type get_cached: bool

        :return: Keys are the integer partition strings, values are the
            :py:class:`.tensor_operator.TensorOperator` objects of the corresponding
            Young projectors.
        :rtype: dict
        """
        if get_cached:
            projectors = self.retrieve_projectors(dimension=dimension, degree=degree)
            return projectors

        character_table = CharacterTable(degree=degree)
        logger.debug('Grouping permutations on %s elements into conjugacy classes.', degree)
        conjugacy_classes = character_table.get_conjugacy_classes()
        aggregated_permutation_operators = {
            partition_string : TensorOperator(
                number_of_factors=degree,
                dimension=dimension,
            ) for partition_string in conjugacy_classes.keys()
        }
        logger.debug('Aggregating permutation operators along %s classes.', len(conjugacy_classes))
        for partition_string, conjugacy_class in conjugacy_classes.items():
            logger.debug('Doing aggregation over %s elements.', len(conjugacy_class))
            for permutation in conjugacy_class:
                aggregated_permutation_operators[partition_string].add(
                    TensorOperator(
                        number_of_factors=degree,
                        dimension=dimension,
                        permutation_inverse=permutation,
                    ),
                    inplace=True
                )
        projectors = {
            key : TensorOperator(
                number_of_factors=degree,
                dimension=dimension,
            ) for key in character_table.get_characters().keys()
        }
        for key, character in character_table.get_characters().items():
            for partition_string, aggregated_operator in aggregated_permutation_operators.items():
                projectors[key].add(
                    aggregated_operator.scale_by(amount=character[partition_string]),
                    inplace=True,
                )
            character_dimension = character[character_table.get_identity_partition_string()]
            projectors[key].scale_by(amount=character_dimension / factorial(degree), inplace=True)
        if not self.validate_projectors(projectors, character_table):
            return None
        return projectors

    def validate_projectors(self,
        projectors: dict=None,
        character_table: CharacterTable=None,
    ):
        """
        :param projectors: The projectors onto isotypic components, as returned by
            :py:meth:`recalculate_projectors`.
        :type projectors: list

        :param character_table: The wrapper object around the character table for the
            symmetric group pertaining to the tensor product space which is the
            projectors' domain.
        :type character_table: CharacterTable

        :return: True if projectors sum to identity (within an error tolerance), else
            False.
        :rtype: bool
        """
        identity = character_table.get_identity_partition_string()
        degree = int(len(projectors[identity].data.shape) / 2)
        dimension = projectors[identity].data.shape[2]
        accumulator = TensorOperator(
            number_of_factors=degree,
            dimension=dimension,
        )
        for projector in projectors.values():
            accumulator.add(projector, inplace=True)
        identity_scaled = TensorOperator(
            number_of_factors=degree,
            dimension = dimension,
            identity = True,
        )
        tolerance = np.linalg.norm(accumulator.data) / pow(10, 9)
        if not np.linalg.norm(accumulator.data - identity_scaled.data) < tolerance:
            logger.error('Projectors do not sum to identity.')
            logger.error(
                'Norm of defect: %s',
                np.linalg.norm(accumulator.data - identity_scaled.data),
            )
            return False
        else:
            logger.debug('Projectors sum to identity.')
            return True

    def recenter_at_mean(self,
        samples,
    ):
        """
        :param samples: "Registered" spatial samples data. A multi-dimensional array, or
            nested list of lists of lists. The axis indices are respectively:

            - the index indicating the series/variable
            - the sample index
            - the spatial coordinate index

        :type samples: multi-dimensional array-like

        :return: Same as ``samples``, except that a translation is applied to each
            spatial variable which results in the new variable having mean vector equal
            to 0.
        :rtype: numpy.array
        """
        degree = samples.shape[0]
        number_of_samples = samples.shape[1]
        dimension = samples.shape[2]
        means = np.array(
            [[np.mean(samples[i,:,a]) for a in range(dimension)] for i in range(degree)]
        )
        recentered = np.zeros(samples.shape)
        for i in range(degree):
            for a in range(dimension):
                m = means[i,a]
                for j in range(number_of_samples):
                    recentered[i,j,a] = samples[i,j,a] - m
        return recentered

    def calculate_covariance_tensor(self, samples):
        """
        :param samples: "Registered" spatial samples data. A multi-dimensional array, or
            nested list of lists of lists. The axis indices are respectively:

            - the index indicating the series/variable
            - the sample index
            - the spatial coordinate index

        :type samples: multi-dimensional array-like

        :return: The joint moment of the spatial variables.
        :rtype: Tensor
        """
        degree = samples.shape[0]
        number_of_samples = samples.shape[1]
        dimension = samples.shape[2]
        covariance_tensor = Tensor(
            number_of_factors=degree,
            dimension=dimension,
        )
        it = covariance_tensor.get_entry_iterator()
        for entry in it:
            M = it.multi_index
            it[0] = np.sum([
                np.prod([
                    samples[i, j, M[i]] for i in range(degree)
                ]) for j in range(number_of_samples)
            ])
        if (covariance_tensor.data == 0).all():
            logger.warning('Covariance tensor is identically 0.')
        return covariance_tensor

    def calculate_decomposition(self,
        tensor,
        projectors,
    ):
        """
        :param tensor: Input tensor to be decomposed.
        :type tensor: Tensor

        :param projectors: Projector operators onto isotypic components, as returned by
            :py:meth:`recalculate_projectors`.
        :type projectors: dict

        :return: Keys are the integer partition strings labelling isotypic components,
            values are the components of the input tensor, as :py:class:`.tensor.Tensor`
            objects.
        :rtype: dict
        """
        degree = len(tensor.data.shape)
        decomposition = {}
        for partition_string, projector in projectors.items():
            component = projector.apply(tensor)
            decomposition[partition_string] = component
        return decomposition

    def validate_decomposition(self, decomposition, tensor):
        """
        :param decomposition: Additive Schur-Weyl decomposition, as returned e.g. by
            :py:meth:`calculate_decomposition`.
        :type decomposition: dict

        :param tensor: A given tensor.
        :type tensor: Tensor

        :return: True if the sum of the components of the decomposition equals to the
            supplied tensor (within an error tolerance).
        :rtype: bool
        """
        degree = len(tensor.data.shape)
        dimension = tensor.data.shape[0]
        resummed = Tensor(
            number_of_factors = degree,
            dimension = dimension,
        )
        for i, component in decomposition.items():
            resummed.add(component, inplace=True)
        tolerance = np.linalg.norm(tensor.data) / pow(10, 9)
        if not np.linalg.norm(resummed.data - tensor.data) < tolerance:
            logger.error('Components do not sum to original tensor.')
            logger.error('Norm of defect: %s', np.linalg.norm(resummed.data - tensor.data))
            logger.error('Norm of original tensor: %s', np.linalg.norm(tensor.data))
            return False
        else:
            logger.debug('Components sum to original tensor.')
            return True

    @staticmethod
    def format_projectors_filename(degree, dimension):
        return '_'.join([
            'projectors',
            'degree',
            str(degree),
            'dimension',
            str(dimension) + '.npz',
        ])

    def retrieve_projectors(self, dimension: int=None, degree: int=None):
        """
        Retrieve projectors from archived numpy-exported files.

        :param dimension: Spatial dimension.
        :type dimension: int

        :param degree: Degree of symmetric group.
        :type degree: int

        :return: Dictionary with keys the '+'-delimited integer partitions and values
            the :py:class:`.tensor_operator.TensorOperator` projectors.
        :rtype: dict
        """
        if degree > SchurTransform.max_degree:
            logger.error('Can not retrieve projectors from cache for degree %s', degree)
            return
        if dimension > SchurTransform.max_dimension:
            logger.error('Can not retrieve projectors from cache for dimension %s', dimension)
            return

        filename = SchurTransform.format_projectors_filename(degree, dimension)
        with importlib.resources.path(package=projectors_package, resource=filename) as path:
            projectors_npy = np.load(path)

        projectors = {key : TensorOperator(
            number_of_factors = degree,
            dimension = dimension,
            data = projectors_npy[key],
        ) for key in projectors_npy}

        return projectors


def save_projectors_to_file():
    """
    Pre-calculates the projectors and saves to numpy archive format.

    The filenames are formatted as in "projectors_degree_5_dimension_3.npz".
    """
    st = SchurTransform()
    for d in range(2, SchurTransform.max_dimension+1):
        for i in range(2, SchurTransform.max_degree+1):
            projectors = st.recalculate_projectors(
                dimension = d,
                degree = i,
                get_cached = False,
            )
            filename = SchurTransform.format_projectors_filename(i, d)
            np.savez(filename, **{key : projector.data for key, projector in projectors.items()})
            logger.info('Saved %s', filename)
