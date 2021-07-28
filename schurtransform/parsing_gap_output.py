#!/usr/bin/env python3
import sys
import re

import pandas as pd


class CharacterTableGAPTextParser:
    """
    Creates simplified character tables from a customized GAP program output.
    """
    def __init__(self, text):
        self.text = text

    def get_ordered_key_value_pairs(self):
        """
        Breaks out the GAP output text into sections.

        :return: A list of (header name, contents) pairs.
        :rtype: list
        """
        pairs = []
        section_pattern_capture = r'^Begin section: ([\w \(\)\.\,]+)(.+?)End section\.$'
        section_pattern = r'Begin section: [\w \(\)\.\,]+.+?End section\.'
        sections = re.findall(section_pattern, self.text, flags=re.DOTALL)
        for section in sections:
            result = re.search(section_pattern_capture, section, flags=re.DOTALL)
            header = result.group(1)
            contents = re.sub('\n', ' ', result.group(2)).strip()
            pairs.append((header, contents))

        return pairs

    def create_tables(self):
        pairs = self.get_ordered_key_value_pairs()
        headers = [
            'Rank of symmetric group',
            'Character function values',
            'Partition labels for the sequence of character functions',
            ''.join([
                'Partition labels for the sequence of conjugacy classes ',
                '(the domain of each character function)',
            ]),
            'Sizes of conjugacy classes',
        ]
        index = {headers[i] : i for i in range(len(headers))}
        tables = {}
        conjugacy_class_records = []
        for i in range(int(len(pairs)/len(headers))):
            I = len(headers)*i
            for j in range(len(headers)):
                if not pairs[I + j][0] == headers[j]:
                    print(
                        ''.join([
                            'Error: Parsing GAP output failed, bad "key" name: ',
                            pairs[I + j][0],
                            ', ',
                            headers[j],
                        ])
                    )
                    return
            rank = pairs[I + index['Rank of symmetric group']][1]
            characters = pairs[I + index['Character function values']][1]
            character_labels = pairs[
                I + index['Partition labels for the sequence of character functions']
            ][1]
            domain_labels = pairs[
                I + index[''.join([
                    'Partition labels for the sequence of conjugacy classes ',
                    '(the domain of each character function)',
                ])]
            ][1]
            class_sizes = pairs[I + index['Sizes of conjugacy classes']][1]

            rank = int(rank)
            parse_partitions = lambda x: [
                [int(s) for s in re.findall(r'[\-\d]+', string)] for string in x
            ]

            characters = re.findall(r'\[ [\-\d \,]+ \]', characters)
            characters = parse_partitions(characters)

            character_labels = re.findall(r'\[ [\-\d \,]+ \]', character_labels)
            character_labels = parse_partitions(character_labels)
            character_labels = [self.transpose_partition(p) for p in character_labels]
            character_labels = [
                '+'.join([str(number) for number in label]) for label in character_labels
            ]

            domain_labels = re.findall(r'\[ [\-\d \,]+ \]', domain_labels)
            domain_labels = parse_partitions(domain_labels)
            domain_labels = [
                '+'.join([str(number) for number in label]) for label in domain_labels
            ]

            class_sizes = [int(match) for match in re.findall(r'\d+', class_sizes)]

            if set(character_labels) != set(domain_labels):
                print(
                    ''.join([
                        'Error: Character labels and domain/conjugacy class labels ',
                        'in GAP output were not exactly equal sets.',
                    ])
                )
                return

            records = {
                character_labels[i] : {
                    domain_labels[j] : characters[i][j] for j in range(len(domain_labels))
                } for i in range(len(character_labels))
            }

            for character_label, function in records.items():
                all_1s = all([value == 1 for domain_label, value in function.items()])
                if all_1s:
                    if character_label != '+'.join(['1']*rank):
                        print(
                            ''.join([
                                'Error: The trivial partition does not match up with',
                                ' the trivial representation in case of rank ',
                                str(rank),
                                '.',
                            ])
                        )

            records = {domain_label : records[domain_label] for domain_label in domain_labels}
            df = pd.DataFrame(records).transpose()
            for j in range(len(domain_labels)):
                conjugacy_class_records.append({
                    'Symmetric group' : 'S' + str(rank),
                    'Partition' : domain_labels[j],
                    'Conjugacy class size' : class_sizes[j],
                })
            tables[rank] = df
        conjugacy_classes = pd.DataFrame(conjugacy_class_records)
        for rank, table in tables.items():
            table.to_csv('s' + str(rank) + '.csv')

        conjugacy_classes.to_csv('symmetric_group_conjugacy_classes.csv', index=False)

    def transpose_partition(self, partition):
        """
        Transposition in the Young diagram sense (a basic duality).

        :param partition: A list of integers representing an integer partition.
        :type partition: list

        :return: The descending-sorted list of integers which is the dual partition.
        :rtype: list
        """
        new_parts = [
            sum([
                1 for part_size in partition if part_size > i
            ]) for i in range(max(partition)*len(partition))
        ]
        new_parts = [part_size for part_size in new_parts if part_size != 0]
        return sorted(new_parts, reverse=True)
