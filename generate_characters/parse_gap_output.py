#!/usr/bin/env python3
import sys
import re

import pandas as pd


class CharacterTableGAPTextParser:
    def __init__(self, text):
        self.text = text

    def get_ordered_key_value_pairs(self):
        pairs = []
        sections = re.findall(r'Begin section: [\w \(\)\.\,]+.+?End section\.', self.text, flags=re.DOTALL)
        for section in sections:
            result = re.search(r'^Begin section: ([\w \(\)\.\,]+)(.+?)End section\.$', section, flags=re.DOTALL)
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
            'Partition labels for the sequence of conjugacy classes (the domain of each character function)',
            'Sizes of conjugacy classes',
        ]
        index = {headers[i] : i for i in range(len(headers))}
        tables = {}
        conjugacy_class_records = []
        for i in range(int(len(pairs)/len(headers))):
            I = len(headers)*i
            for j in range(len(headers)):
                if not pairs[I + j][0] == headers[j]:
                    print('Error: Parsing GAP output failed, bad "key" name: ' + pairs[I + j][0] + ', ' + headers[j])
                    return
            rank = pairs[I + index['Rank of symmetric group']][1]
            characters = pairs[I + index['Character function values']][1]
            character_labels = pairs[I + index['Partition labels for the sequence of character functions']][1]
            domain_labels = pairs[I + index['Partition labels for the sequence of conjugacy classes (the domain of each character function)']][1]
            class_sizes = pairs[I + index['Sizes of conjugacy classes']][1]

            rank = int(rank)
            characters = re.findall(r'\[ [\-\d \,]+ \]', characters)
            characters = [[int(string) for string in re.findall(r'[\-\d]+', character_string)] for character_string in characters]
            character_labels = re.findall(r'\[ [\-\d \,]+ \]', character_labels)
            character_labels = [[int(string) for string in re.findall(r'[\-\d]+', label)] for label in character_labels]
            character_labels = ['+'.join([str(number) for number in label]) for label in character_labels]
            domain_labels = re.findall(r'\[ [\-\d \,]+ \]', domain_labels)
            domain_labels = [[int(string) for string in re.findall(r'[\-\d]+', label)] for label in domain_labels]
            domain_labels = ['+'.join([str(number) for number in label]) for label in domain_labels]
            class_sizes = [int(match) for match in re.findall(r'\d+', class_sizes)]
            if character_labels != domain_labels:
                print('Error: Character labels and domain/conjugacy class labels were not exactly equal in GAP output.')
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
                        print('Error: The trivial partition does not match up with the trivial representation in case of rank ' + str(rank) + '.')

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

input_filename = sys.argv[1]
with open(input_filename) as file:
    text = file.read()

parser = CharacterTableGAPTextParser(text)
parser.create_tables()
