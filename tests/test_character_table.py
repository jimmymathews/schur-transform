from math import factorial

import schurtransform
from schurtransform.character_table import CharacterTable

def test_init():
    for rank in [2,3,4,5,6]:
        table = CharacterTable(rank=rank)
        N = len(table.characters)
        for character in table.characters.values():
            assert(N == len(character))
        domain = table.conjugacy_class_representatives
        sizes = table.conjugacy_class_sizes
        for character1 in table.characters.values():
            for character2 in table.characters.values():
                product = sum([character1[key] * character2[key] * sizes[key] for key in domain])
                print(character1)
                print(character2)
                print(product)
                print('')
                print('\n'.join([str([character1[key], character2[key], sizes[key]]) for key in domain]))
                if character1 != character2:
                    assert(product == 0)
                else:
                    assert(product == factorial(rank))

def test_partitioning_permutation():
    p = CharacterTable.partition_from_permutation(
        permutation=[3, 1, 2, 4, 5, 7, 6, 8, 9, 10]
    )
    assert(p == (1, 1, 1, 1, 1, 2, 3))

def test_build_conjugacy_classes():
    table = CharacterTable(rank=3)
    conjugacy_classes = table.get_conjugacy_classes()
    assert(conjugacy_classes == {
        '1+1+1' : [(1, 2, 3)],
        '2+1' : [(1, 3, 2), (2, 1, 3), (3, 2, 1)],
        '3' : [(2, 3, 1), (3, 1, 2)],
    })
