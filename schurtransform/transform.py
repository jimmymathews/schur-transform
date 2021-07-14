from enum import Enum, auto
from functools import lru_cache
from itertools import combinations
from math import factorial

import numpy as np

from .tensor import Tensor
from .tensor_operator import TensorOperator
from .character_table import CharacterTable
from .log_formats import colorized_logger
logger = colorized_logger(__name__)


class SummaryType(Enum):
    COMPONENTS = auto()
    NORMS = auto()
    CONTENT = auto()
    SEQUENTIAL_CONTENT = auto()
    MEAN_CONTENT = auto()
    VARIANCE_CONTENT = auto()


class SchurTransform:
    def transform(self,
        samples,
        summary_type: str='COMPONENTS',
        number_of_factors: int=None,
        character_table_filename: str=None,
        conjugacy_classes_table_filename: str=None,
    ):
        """
        Args:
            samples (multi dimensional array-like):
                A multi-dimensional array, or nested list of lists of lists. The axis
                indices are respectively: the index indicating the series/variable,
                the sample index, and the spatial coordinate index.
            summary_type (str):
                See the enum class ``SummaryType``, and the cases for return value.
            number_of_factors (int):
                In case of one of the "...CONTENT" summary types, this integer provides
                the number of factors (number of variables) used in the joint moment.
                Currently must be less than or equal to 8, unless you provide your own
                character table and conjugacy class information.
            character_table_filename (str):
                Only provide this argument if you wish to supply a character table for a
                symmetric group of rank higher than 8 (beyond S8). Use the file format
                exemplified by ``s2.csv``, ``s3.csv``, etc. under the
                ``character_tables`` subpackage.
            conjugacy_classes_table_filename (str):
                Only provide this argument if you wish to supply a character table for a
                symmetric group of rank higher than 8 (beyond S8). Use the file format
                exemplified by ``symmetric_group_conjugacy_classes.csv`` in the
                ``character_tables`` subpackage.

        Returns:
            array-like:
                If ``summary_type`` is "COMPONENTS", returns the tensor components of
                the Schur-Weyl decomposition of the joint moment tensor, the tensor
                product over the series index.

                If ``summary_type`` is "NORMS", returns the Euclidean norms of the
                tensor components of the Schur-Weyl decomposition.

                If ``summary_type`` is "CONTENT", returns a list of distributions, one
                for each tensor component type, consisting of the Euclidean norms of
                that component of the decomposition of all N-factor joint moments,
                where N is the given ``number_of_factors``.

                If ``summary_type`` is "SEQUENTIAL_CONTENT", returns a list of
                distributions just as in the CONTENT case, except that only consecutive
                N-fold products are considered.

                If ``summary_type`` is "MEAN_CONTENT", the means of the distributions
                obtained in the "CONTENT" case are provided (one for each tensor
                component type).

                If ``summary_type`` is "VARIANCE_CONTENT", the variances of the
                distributions obtained in the "CONTENT" case are provided.
        """
        if type(samples) is list:
            samples = np.array(samples)

        if len(samples.shape) != 3:
            logger.error('Expected 3 axes: series (random variable), sample, and spatial coordinate. Got axes of sizes: %s', samples.shape)
            return

        number_of_series = samples.shape[0]
        dimension = samples.shape[2]
        summary_type = SummaryType[summary_type]
        if summary_type in [SummaryType.COMPONENTS, SummaryType.NORMS]:
            rank = number_of_series
        else:
            rank = number_of_factors
            if number_of_factors is None:
                logger.error(
                    'For summary_type=%s you must supply a number of tensor factors.',
                    summary_type.name,
                )
                return

        logger.debug(
            'Calculating projectors of type rank=%s and dimension=%s.',
            rank,
            dimension,
        )
        projectors = self.recalculate_projectors(
            dimension=dimension,
            rank=rank,
        )
        if summary_type in [SummaryType.COMPONENTS, SummaryType.NORMS]:
            centered = self.recenter_at_mean(samples)
            covariance_tensor = self.calculate_covariance_tensor(centered)
            decomposition = self.calculate_decomposition(covariance_tensor, projectors)
            self.validate_decomposition(decomposition, covariance_tensor)

            if summary_type == SummaryType.COMPONENTS:
                return decomposition

            if summary_type == SummaryType.NORMS:
                return {i: np.linalg.norm(component.data) for i, component in decomposition.items()}

        if summary_type in [
            SummaryType.CONTENT,
            SummaryType.SEQUENTIAL_CONTENT,
            SummaryType.MEAN_CONTENT,
            SummaryType.VARIANCE_CONTENT,
        ]:
            if summary_type == SummaryType.SEQUENTIAL_CONTENT:
                index_combinations = [[i + j for j in range(rank)] for i in range(number_of_series-(rank-1))]
            else:
                index_combinations = combinations(list(range(number_of_series)), rank)

            character_table = CharacterTable(rank=rank)
            content = {key : [] for key in character_table.get_characters().keys()}
            for combination in index_combinations:
                subsample = samples[list(combination), :, :]
                centered = self.recenter_at_mean(subsample)
                covariance_tensor = self.calculate_covariance_tensor(centered)
                decomposition = self.calculate_decomposition(covariance_tensor, projectors)
                self.validate_decomposition(decomposition, covariance_tensor)
                norms = {i: np.linalg.norm(component.data) for i, component in decomposition.items()}
                for i, norm in norms.items():
                    content[i].append(norm)

            if summary_type is SummaryType.CONTENT:
                return content
            if summary_type is SummaryType.SEQUENTIAL_CONTENT:
                return content
            if summary_type is SummaryType.MEAN_CONTENT:
                return {i : np.mean(content[i]) for i in content.keys()}
            if summary_type is SummaryType.VARIANCE_CONTENT:
                return {i : np.var(content[i]) for i in content.keys()}

    @lru_cache(maxsize=1)
    def recalculate_projectors(self,
        dimension: int=None,
        rank: int=None,
    ):
        """
        Args:                
            dimension (int):
                The dimension of the base vector space.
            rank (int):
                The number of factors in the tensor product.

        Returns:
            dict:
                Keys are the integer partition strings, values are the TensorOperator
                objects of the corresponding Young projectors.
        """
        character_table = CharacterTable(rank=rank)
        conjugacy_classes = character_table.get_conjugacy_classes()
        aggregated_permutation_operators = {
            partition_string : TensorOperator(
                number_of_factors=rank,
                dimension=dimension,
            ) for partition_string in conjugacy_classes.keys()
        }
        for partition_string, conjugacy_class in conjugacy_classes.items():
            for permutation in conjugacy_class:
                aggregated_permutation_operators[partition_string].add(
                    TensorOperator(
                        number_of_factors=rank,
                        dimension=dimension,
                        permutation_inverse=permutation,
                    ),
                    inplace=True
                )
        projectors = {
            key : TensorOperator(
                number_of_factors=rank,
                dimension=dimension,
            ) for key in character_table.get_characters().keys()
        }
        for key, character in character_table.get_characters().items():
            for partition_string, aggregated_permutation_operator in aggregated_permutation_operators.items():
                projectors[key].add(
                    aggregated_permutation_operator.scale_by(amount=character[partition_string]),
                    inplace=True,
                )
            character_dimension = character[character_table.get_identity_partition_string()]
            projectors[key].scale_by(amount=character_dimension / factorial(rank), inplace=True)
        if not self.validate_projectors(projectors, character_table):
            return None
        return projectors

    def validate_projectors(self,
        projectors: dict=None,
        character_table: CharacterTable=None,
    ):
        """
        Args:
            projectors (dict):
                The projectors onto isotypic components, as returned by
                ``recalculate_projectors``.
            character_table (CharacterTable):
                The wrapper object around the character table for the symmetric group
                pertaining to the tensor product space which is the projectors' domain.

        Returns:
            bool:
                True if projectors sum to identity (within an error tolerance), else
                False.
        """
        identity = character_table.get_identity_partition_string()
        rank = int(len(projectors[identity].data.shape) / 2)
        dimension = projectors[identity].data.shape[2]
        accumulator = TensorOperator(
            number_of_factors=rank,
            dimension=dimension,
        )
        for projector in projectors.values():
            accumulator.add(projector, inplace=True)
        identity_scaled = TensorOperator(
            number_of_factors=rank,
            dimension = dimension,
            identity = True,
        )
        tolerance = np.linalg.norm(accumulator.data) / pow(10, 9)
        if not np.linalg.norm(accumulator.data - identity_scaled.data) < tolerance:
            logger.error('Projectors do not sum to identity.')
            logger.error('Norm of defect: %s', np.linalg.norm(accumulator.data - identity_scaled.data))
            return False
        else:
            logger.debug('Projectors sum to identity.')
            return True

    def recenter_at_mean(self, samples):
        """
        Args:
            samples (np.array):
                "Registered" spatial samples data.

        Returns:
            Same as samples, except that a translation is applied to each variable which
            results in the new variable having mean vector equal to 0.
        """
        rank = samples.shape[0]
        number_of_samples = samples.shape[1]
        dimension = samples.shape[2]
        means = np.array([[np.mean(samples[i,:,a]) for a in range(dimension)] for i in range(rank)])
        recentered = np.zeros(samples.shape)
        for i in range(rank):
            for a in range(dimension):
                m = means[i,a]
                for j in range(number_of_samples):
                    recentered[i,j,a] = samples[i,j,a] - m
        return recentered

    def calculate_covariance_tensor(self, samples):
        """
        Args:
            samples (np.array):
                "Registered" spatial samples data, typically with mean 0 for each
                spatial variable.

        Returns:
            Tensor:
                The joint moment of the spatial variables.
        """
        rank = samples.shape[0]
        number_of_samples = samples.shape[1]
        dimension = samples.shape[2]
        covariance_tensor = Tensor(
            number_of_factors=rank,
            dimension=dimension,
        )
        it = covariance_tensor.get_entry_iterator()
        for entry in it:
            M = it.multi_index
            it[0] = np.sum([
                np.prod([
                    samples[i, j, M[i]] for i in range(rank)
                ]) for j in range(number_of_samples)
            ])
        if (covariance_tensor.data == 0).all():
            logger.warning('Covariance tensor is identically 0.')
        return covariance_tensor

    def calculate_decomposition(self, tensor, projectors):
        """
        Args:
            tensor (Tensor):
                Input tensor to be decomposed.
            projectors (dict):
                Projector operators onto isotypic components, as returned by
                ``recalculate_projectors``.

        Returns:
            dict:
                Keys are the integer partition strings labelling isotypic components,
                values are the components of the input tensor in the given component.
        """
        rank = len(tensor.data.shape)
        decomposition = {}
        for partition_string, projector in projectors.items():
            component = projector.apply(tensor)
            decomposition[partition_string] = component
        return decomposition

    def validate_decomposition(self, decomposition, tensor):
        """
        Args:
            decomposition (dict):
                Additive Schur-Weyl decomposition, as returned e.g. by
                ``calculate_decomposition``.
            tensor (Tensor):
                A given tensor.

        Returns:
            bool:
                True if the sum of the components of the decomposition equals to the
                supplied tensor (within an error tolerance).
        """
        rank = len(tensor.data.shape)
        dimension = tensor.data.shape[0]
        resummed = Tensor(
            number_of_factors = rank,
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
