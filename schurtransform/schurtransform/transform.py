import enum
from enum import Enum, auto
import os
from os.path import join
import functools
from functools import lru_cache
import math
from math import factorial

import numpy as np

from .symmetric_group_utilities import SymmetricGroupUtilities
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
        summary_type: SummaryType=SummaryType.COMPONENTS,
        number_of_factors: int=None,
    ):
        """
        Args:
            samples (multi dimensional array-like):
                A multi-dimensional array, or nested list of lists of lists. The axis
                indices are respectively: the index indicating the series, the sample
                index, and the spatial coordinate index.
            summary_type (SummaryType):
                See cases for return value.
            number_of_factors (int):
                In case of one of the "...CONTENT" summary types, this integer provides
                the number of factors (number of series) used in the joint moment.
                Currently must be less than or equal to 6.
        Returns:
            array-like:
                If ``summary_type`` is COMPONENTS, returns the tensor components of the Schur-Weyl decomposition of the joint moment tensor, the tensor product over the series index.
                If ``summary_type`` is NORMS, returns the Euclidean norms of the tensor components of the Schur-Weyl decomposition.
                If ``summary_type`` is CONTENT, returns a list of distributions, one for each tensor component type, consisting of the Euclidean norms of that component of the decomposition of all N-factor joint moments, where N is the given ``number_of_factors``.
                If ``summary_type`` is SEQUENTIAL_CONTENT, returns a list of distributions just as in the CONTENT case, except that only consecutive N-fold products are considered.
                If ``summary_type`` is MEAN_CONTENT, the means of the distributions obtained in the CONTENT case are provided (one for each tensor component type).
                If ``summary_type`` is VARIANCE_CONTENT, the variances of the distributions obtained in the CONTENT case are provided.
        """
        if type(samples) is list:
            samples = np.array(samples)

        if len(samples.shape) != 3:
            logger.error('Expected 3 axes: series, sample, and spatial coordinate. Got axes of sizes: %s', samples.shape)
            return
        number_of_series = samples.shape[0]
        number_of_samples= samples.shape[1]
        dimension = samples.shape[2]

        if summary_type in [SummaryType.COMPONENTS, SummaryType.NORMS]:
            order = number_of_series
        else:
            order = number_of_factors
            if number_of_factors is None:
                logger.error(
                    'For summary_type=%s you must supply a number of tensor factors.',
                    summary_type.name,
                )
                return

        projectors = self.recalculate_projectors(
            number_of_samples=number_of_samples,
            dimension=dimension,
            order=order,
        )

        if summary_type in [SummaryType.COMPONENTS, SummaryType.NORMS]:
            centered = self.recenter_at_mean(samples)
            covariance_tensor = self.calculate_covariance_tensor(centered)
            decomposition = self.calculate_decomposition(covariance_tensor, projectors)
            if not self.validate_decomposition(decomposition):
                return

            if summary_type == SummaryType.COMPONENTS:
                return decomposition

            if summary_type == SummaryType.NORMS:
                return {i: np.linalg.norm(component.data) for i, component in decomposition.items()}

    @lru_cache(maxsize=1)
    def recalculate_projectors(self,
        number_of_samples: int=None,
        dimension: int=None,
        order: int=None,
    ):
        symmetric_group = SymmetricGroupUtilities(order=order)
        conjugacy_classes = symmetric_group.compute_conjugacy_classes()
        aggregated_permutation_operators = {
            cycle_type : TensorOperator(
                number_of_factors=order,
                dimension=dimension,
            ) for cycle_type in conjugacy_classes.keys()
        }
        for cycle_type, conjugacy_class in conjugacy_classes.items():
            for permutation in conjugacy_class:
                aggregated_permutation_operators[cycle_type].add(
                    TensorOperator(
                        number_of_factors=order,
                        dimension=dimension,
                        permutation_inverse=permutation,
                    ),
                    inplace=True
                )
        projectors = {
            i : TensorOperator(
                number_of_factors=order,
                dimension=dimension,
            ) for i in range(len(symmetric_group.characters))
        }
        for i, character in enumerate(symmetric_group.characters):
            for cycle_type, aggregated_permutation_operator in aggregated_permutation_operators.items():
                projector[i].add(
                    aggregated_permutation_operator.scale_by(character[cycle_type])
                )
            projector[i].scale_by(character['()'], inplace=True)
        if not self.validate_projectors(projectors, symmetric_group):
            return None
        return projectors

    def validate_projectors(self, projectors, symmetric_group):
        order = len(projectors[0].data.shape) / 2
        dimension = projectors[0].data.shape[2]
        accumulator = TensorOperator(
            number_of_factors=order,
            dimension=dimension,
        )
        for projector in projectors.values():
            accumulator.add(projector, inplace=True)

        identity_scaled = TensorOperator(
            number_of_factors=order,
            dimension = dimension,
            identity = True,
        )
        identify_scaled.scale_by(factorial(order), inplace=True)

        if not (accumulator.data == identity_scaled.data).all():
            logger.error('Projects do not sum to identity.')
            return False
        else:
            return True

    def recenter_at_mean(self, samples):
        order = samples.shape[0]
        number_of_samples = samples.shape[1]
        dimension = samples.shape[2]
        means = np.array([[np.mean(samples[i,:,a]) for a in range(dimension)] for i in range(order)])

        recentered = np.array(samples.shape)
        for i in range(order):
            for a in range(dimension):
                m = means[i,a]
                for j in range(number_of_samples):
                    recentered[i,j,a] = samples[i,j,a] - m
        return recentered

    def calculate_covariance_tensor(self, samples):
        order = samples.shape[0]
        number_of_samples = samples.shape[1]
        dimension = samples.shape[2]
        covariance_tensor = Tensor(
            number_of_factors=order,
            dimension=dimension,
        )
        it = covariance_tensor.entry_iterator()
        for entry in it:
            M = it.multi_index
            it[0] = np.sum([
                np.prod([
                    samples[i, j, M[i]] for i in range(order)
                ]) for j in range(number_of_samples)
            ])
        return covariance_tensor

    def calculate_decomposition(self, tensor, projectors):
        order = tensor.data.shape[0]
        self.decomposition = {}
        for i, projector in projectors.items():
            component = projector.apply(tensor)
            component.scale_by(1.0/factorial(order), inplace=True)
            self.decomposition[i] = component

    def validate_decomposition(self, decomposition, tensor):
        order = tensor.data.shape[0]
        dimension = tensor.data.shape[2]
        resummed = Tensor(
            number_of_factors = order,
            dimension = dimension,
        )
        for i, component in decomposition.items():
            resummed.add(component, inplace=True)
        if not (resummed.data == tensor.data).all():
            logger.error('Components do not sum to original tensor.')
            return False
        else:
            return True
