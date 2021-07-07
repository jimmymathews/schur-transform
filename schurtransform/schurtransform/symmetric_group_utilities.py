import itertools
import importlib
import importlib.resources
import re

import pandas as pd

from . import character_tables
from .log_formats import colorized_logger
logger = colorized_logger(__name__)


class SymmetricGroupUtilities:
    """
    Helper functions for working with permutation groups and their characters.
    """
    def __init__(self,
        order: int=None,
    ):
        """
        Attributes:
            conjugacy_class_representatives (list):
                Strings in cycle notation indicating conjugacy classes in the symmetric
                group.
            conjugacy_class_sizes (dict):
                The sizes of each conjugacy class.
            characters (list):
                A list of dictionaries, each dictionary being the class function
                represented by one character of the symmetric group of order ``order``.

        Args:
            order (int):
                The order of the symmetric group to be considered.
        """  
        self.order = order
        if self.order < 2:
            logger.error('Need order > 1, got %s', order)
            return
        if self.order > 6:
            logger.error('Regeneration not supported yet (only orders up to 6 are distributed with the library).')
            return

        with importlib.resources.path(character_tables, 's' + str(order) + '.csv') as path:
            df = pd.read_csv(path, header=None)
        self.characters = []
        self.conjugacy_class_representatives = list(df.iloc[1])
        keys = self.conjugacy_class_representatives
        conjugacy_class_sizes = list(df.iloc[0])
        self.conjugacy_class_sizes = {keys[i]:int(conjugacy_class_sizes[i]) for i in range(len(keys))}
        for i, row in df.iterrows():
            if i < 2:
                continue
            self.characters.append({keys[i]:int(row[i]) for i in range(len(row))})

    @staticmethod
    def partition_from_cycle_type(
        cycle_type: str=None,
        partitioned_integer: int=None,
    ):
        """
        Args:
            cycle_type (str):
                The format should be as in '(1 2)(3 4)'. The parentheses are mandatory,
                and the spacing is somewhat optional in that other characters may be
                used as spacers as long as they are non-digits.
            partitioned_integer (int):
                The integer partitioned (i.e. the largest integer which would appear in
                a complete cycle notation in which length-one cycles are included.)

        Returns:
            list:
                The sorted list of integers which partition ``partitioned_integer``,
                represented by the given cycle type.
        """
        cycles = re.findall(r'\(([\s\d]+)\)', cycle_type)
        if(len(cycles)<1):
            return tuple([1 for i in range(partitioned_integer)])

        partition = []
        for cycle in cycles:
            numbers = re.findall(r'(\d+)', cycle)
            partition.append(len(numbers))

        return tuple(sorted(partition + [1 for w in range(partitioned_integer - sum(partition))]))

    @staticmethod
    def partition_from_permutation(permutation):
        """
        Args:
            permutation (list):
                A list of positive integers providing the values of a permutation function of an input set of 1-indexed integers.

        Returns:
            list:
                A sorted list of integers that are the cycle lengths of the permutation.
        """
        if sorted(permutation) != [i + 1 for i in range(len(permutation))]:
            logger.error('Permutation must be in positive-integer value-list format.')
            return
        by_index = {i : permutation[i]-1 for i in range(len(permutation))}
        cycles = []
        while len(by_index) > 0:
            index = list(by_index)[0]
            cycle = [by_index[index]]
            next_index = by_index[cycle[-1]]
            while not next_index in cycle:
                cycle.append(next_index)
                next_index = by_index[cycle[-1]]
            cycles.append(cycle)
            for entry in cycle:
                del by_index[entry]
        return tuple(sorted([len(cycle) for cycle in cycles]))

    def compute_conjugacy_classes(self):
        """
        Returns:
            dict:
                Keys are the cycle type strings (as given in the character tables), and
                values are the permutations in the indicated conjugacy class. The format
                of the permutations is a sequence of positive integer function values.
        """
        cycle_types = self.conjugacy_class_representatives
        permutations_by_cycle_type = {
            cycle_type : [] for cycle_type in cycle_types
        }
        cycle_types_by_partition = {
            self.partition_from_cycle_type(
                cycle_type=cycle_type,
                partitioned_integer = self.order,
            ) : cycle_type for cycle_type in cycle_types
        }
        permutations = list(itertools.permutations([i+1 for i in range(self.order)]))
        for permutation in permutations:
            partition = self.partition_from_permutation(permutation)
            cycle_type = cycle_types_by_partition[partition]
            permutations_by_cycle_type[cycle_type].append(permutation)

        for cycle_type, conjugacy_class in permutations_by_cycle_type.items():
            if len(conjugacy_class) != self.conjugacy_class_sizes[cycle_type]:
                logger.error("Found %s permutations of certain class, expected %s.",
                    len(conjugacy_class),
                    self.conjugacy_class_sizes[cycle_type],
                )

        return {key : sorted(value) for key, value in permutations_by_cycle_type.items()}
