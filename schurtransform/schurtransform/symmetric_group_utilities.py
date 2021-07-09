import itertools
import importlib
import importlib.resources
import functools
from functools import lru_cache
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
            logger.error('Need order > 1, got %s.', order)
            return
        if self.order > 8:
            logger.error('Regeneration not supported yet (only orders up to 8 are distributed with the library; see "generate_characters.sh").')
            return

        with importlib.resources.path(character_tables, 's' + str(order) + '.csv') as path:
            character_table = pd.read_csv(path, index_col=0)

        with importlib.resources.path(character_tables, 'symmetric_group_conjugacy_classes.csv') as path:
            conjugacy_classes = pd.read_csv(path, index_col=False)

        conjugacy_classes = conjugacy_classes[conjugacy_classes['Symmetric group'] == 'S' + str(self.order)]
        self.conjugacy_class_sizes = {}
        for i, row in conjugacy_classes.iterrows():
            self.conjugacy_class_sizes[row['Partition']] = row['Conjugacy class size']

        self.conjugacy_class_representatives = [str(entry) for entry in list(conjugacy_classes['Partition'])]

        self.characters = {}
        for index, row in character_table.iterrows():
            self.characters[index] = {
                key : row[key] for key in row.keys()
            }

        # self.conjugacy_class_representatives = list(df.iloc[1])
        # keys = self.conjugacy_class_representatives
        # conjugacy_class_sizes = list(df.iloc[0])

        # self.conjugacy_class_sizes = {keys[i]:int(conjugacy_class_sizes[i]) for i in range(len(keys))}
        # for i, row in df.iterrows():
        #     if i < 2:
        #         continue
        #     self.characters.append({keys[i]:int(row[i]) for i in range(len(row))})

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

    def get_identity_partition_string(self):
        return '+'.join(['1']*self.order)

    def get_characters(self):
        return self.characters

    @lru_cache(maxsize=1)
    def get_conjugacy_classes(self):
        """
        Returns:
            dict:
                Keys are the integer partition strings (as given in the character
                tables), and values are the permutations in the indicated conjugacy
                class. The format of the permutations is a sequence of positive integer
                function values.
        """
        partition_strings = self.conjugacy_class_representatives
        partition_strings_by_partition = {
            tuple(sorted([
                int(entry) for entry in partition_string.split('+')
            ])) : partition_string for partition_string in partition_strings
        }
        permutations_by_partition_string = {
            partition_string : [] for partition_string in partition_strings
        }
        permutations = list(itertools.permutations([i+1 for i in range(self.order)]))
        for permutation in permutations:
            partition = self.partition_from_permutation(permutation)
            partition_string = partition_strings_by_partition[partition]
            permutations_by_partition_string[partition_string].append(permutation)

        for partition_string, conjugacy_class in permutations_by_partition_string.items():
            if len(conjugacy_class) != self.conjugacy_class_sizes[partition_string]:
                logger.error("Found %s permutations of certain class, expected %s.",
                    len(conjugacy_class),
                    self.conjugacy_class_sizes[cycle_type],
                )

        return {key : sorted(value) for key, value in permutations_by_partition_string.items()}
