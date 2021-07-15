import itertools
import importlib.resources
from functools import lru_cache
import re

import pandas as pd

from . import character_tables
from .log_formats import colorized_logger
logger = colorized_logger(__name__)


class CharacterTable:
    """
    Wrapper over a GAP-provided symmetric group character table.
    """
    def __init__(self,
        degree: int=None,
    ):
        """
        :param degree:
            The degree of the symmetric group to be considered.
        :type degree: int
        """  
        self.degree = degree
        if self.degree < 2:
            logger.error('Need degree > 1, got %s.', degree)
            return
        if self.degree > 8:
            logger.error('Regeneration not supported yet (only degrees up to 8 are distributed with the library; see "generate_characters.sh").')
            return

        with importlib.resources.path(character_tables, 's' + str(degree) + '.csv') as path:
            character_table = pd.read_csv(path, index_col=0)

        with importlib.resources.path(character_tables, 'symmetric_group_conjugacy_classes.csv') as path:
            conjugacy_classes = pd.read_csv(path, index_col=False)

        conjugacy_classes = conjugacy_classes[conjugacy_classes['Symmetric group'] == 'S' + str(self.degree)]
        self.conjugacy_class_sizes = {}
        for i, row in conjugacy_classes.iterrows():
            self.conjugacy_class_sizes[row['Partition']] = row['Conjugacy class size']

        self.conjugacy_class_representatives = [str(entry) for entry in list(conjugacy_classes['Partition'])]

        self.characters = {}
        for index, row in character_table.iterrows():
            self.characters[index] = {
                key : row[key] for key in row.keys()
            }

    @staticmethod
    def partition_from_permutation(permutation):
        """
        :param permutation:
            A list of positive integers providing the values (in order) of a permutation
            function of an input set of 1-indexed integers.
        :type permutation: list

        :return:
            A sorted list of integers that are the cycle lengths of the permutation.
        :rtype: list
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
        """
        :return:
            The string representing the identity partition for the given degree.
        :rtype: str
        """
        return '+'.join(['1'] * self.degree)

    def get_characters(self):
        """
        :return:
            A dictionary of dictionaries, each dictionary being the class function
            represented by one character of the symmetric group of degree ``degree``.
            The keys (at both levels) are '+'-delimited integer partition strings.
        :rtype: dict
        """
        return self.characters

    @lru_cache(maxsize=1)
    def get_conjugacy_classes(self):
        """
        :return:
            The literal conjugacy classes of permutations of the given degree. The keys
            are '+'-delimited integer partition strings (as given in the character
            tables), and values are the permutations in the indicated conjugacy class.
            The format of the permutations is a sequence of positive integer function
            values.
        :rtype: dict
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
        permutations = list(itertools.permutations([i+1 for i in range(self.degree)]))
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
