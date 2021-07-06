import numpy as np

import schurtransform
from schurtransform.tensor import Tensor

def test_creation():
    for i in range(5):
        for j in range(5):
            tensor = Tensor(number_of_factors=i+1, dimension=j+1)
            values = list(np.ravel(tensor.data))
            assert(all([element == 0 for element in values]))

def test_iteration_read():
    tensor = Tensor(number_of_factors=4, dimension=3)
    it = tensor.get_entry_iterator()
    for entry in it:
        assert(entry == 0.0)

def test_iteration_write():
    tensor = Tensor(number_of_factors=4, dimension=3)

    writer = tensor.get_entry_iterator()
    for entry in writer:
        if writer.multi_index[0] == 1:
            writer[0] = 1.0

    reader = tensor.get_entry_iterator()
    for entry in reader:
        if reader.multi_index[0] == 1:
            assert(entry == 1.0)
        else:
            assert(entry == 0.0)

def test_arithmetic():
    tensor1 = Tensor(number_of_factors=4, dimension=3)
    writer = tensor1.get_entry_iterator()
    for entry in writer:
        if writer.multi_index[0] == 1:
            writer[0] = 1.0

    tensor2 = Tensor(number_of_factors=4, dimension=3)
    writer = tensor2.get_entry_iterator()
    for entry in writer:
        if writer.multi_index[0] == 1:
            writer[0] = 2.0
    tensor3 = tensor1.add(tensor2)
    tensor4 = tensor3.scale_by(amount=7.0)

    reader = tensor4.get_entry_iterator()
    for entry in reader:
        if reader.multi_index[0] == 1:
            assert(entry == 21.0)
        else:
            assert(entry == 0.0)

    tensor1.add(tensor2, inplace=True)
    tensor1.scale_by(amount=7.0, inplace=True)

    reader = tensor1.get_entry_iterator()
    for entry in reader:
        if reader.multi_index[0] == 1:
            assert(entry == 21.0)
        else:
            assert(entry == 0.0)
