import math
from math import factorial

import schurtransform
from schurtransform.symmetric_group_utilities import SymmetricGroupUtilities

def test_init():
    for order in [2,3,4,5,6]:
        u = SymmetricGroupUtilities(order=order)
        N = len(u.characters)
        for character in u.characters.values():
            assert(N == len(character))
        domain = u.conjugacy_class_representatives
        sizes = u.conjugacy_class_sizes
        for character1 in u.characters.values():
            for character2 in u.characters.values():
                product = sum([character1[key] * character2[key] * sizes[key] for key in domain])
                print(character1)
                print(character2)
                print(product)
                print('')
                print('\n'.join([str([character1[key], character2[key], sizes[key]]) for key in domain]))
                if character1 != character2:
                    assert(product == 0)
                else:
                    assert(product == factorial(order))

# def test_partitioning_cycle_type():
#     u = SymmetricGroupUtilities(order=5)

#     p = u.partition_from_cycle_type(
#         cycle_type='(1 2)(3 4)',
#         partitioned_integer=4,
#     )
#     assert(p == (2, 2))

#     p = u.partition_from_cycle_type(
#         cycle_type='(3 2 1)(6 7)',
#         partitioned_integer=10,
#     )
#     assert(p == (1, 1, 1, 1, 1, 2, 3))

#     p = SymmetricGroupUtilities.partition_from_cycle_type(
#         cycle_type='(3 2 1)(6 7)',
#         partitioned_integer=10,
#     )
#     assert(p == (1, 1, 1, 1, 1, 2, 3))

def test_partitioning_permutation():
    p = SymmetricGroupUtilities.partition_from_permutation(
        permutation=[3, 1, 2, 4, 5, 7, 6, 8, 9, 10]
    )
    assert(p == (1, 1, 1, 1, 1, 2, 3))

def test_build_conjugacy_classes():
    u = SymmetricGroupUtilities(order=3)
    conjugacy_classes = u.get_conjugacy_classes()
    assert(conjugacy_classes == {
        '1+1+1' : [(1, 2, 3)],
        '1+2' : [(1, 3, 2), (2, 1, 3), (3, 2, 1)],
        '3' : [(2, 3, 1), (3, 1, 2)],
    })
