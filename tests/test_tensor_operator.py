import numpy as np
import random
from itertools import combinations

import schurtransform
from schurtransform.tensor import Tensor
from schurtransform.tensor_operator import TensorOperator


def test_creation():
    for i in range(3):
        for j in range(3):
            operator = TensorOperator(number_of_factors=i+1, dimension=j+1)
            values = list(np.ravel(operator.data))
            assert(all([element == 0 for element in values]))

def test_identity():
    tensor = Tensor(number_of_factors=3, dimension=2)
    writer = tensor.get_entry_iterator()
    for entry in writer:
        writer[0] = random.random()

    operator = TensorOperator(number_of_factors=3, dimension=2, identity=True)
    output = operator.apply(tensor)
    reader = output.get_entry_iterator()
    for entry in reader:
        I = reader.multi_index
        assert(entry == tensor.data[I[0], I[1], I[2]])

def test_permutation():
    tensor = Tensor(number_of_factors=3, dimension=2)
    writer = tensor.get_entry_iterator()
    for entry in writer:
        writer[0] = random.random()

    p = [2, 3, 1]
    operator = TensorOperator(number_of_factors=3, dimension=2, permutation_inverse=p)
    output = operator.apply(tensor)
    reader = output.get_entry_iterator()
    for entry in reader:
        I = reader.multi_index
        assert(entry == tensor.data[I[p[0]-1], I[p[1]-1], I[p[2]-1]])

def test_arithmetic():
    tensor = Tensor(number_of_factors=3, dimension=2)
    writer = tensor.get_entry_iterator()
    for entry in writer:
        writer[0] = random.random()

    operator1 = TensorOperator(number_of_factors=3, dimension=2, identity=True)
    operator2 = TensorOperator(number_of_factors=3, dimension=2, identity=True)
    operator3 = operator1.scale_by(amount=3.0)
    operator4 = operator2.scale_by(amount=5.0)

    linear_combination = operator3.add(operator4)
    output = linear_combination.apply(tensor)

    reader = output.get_entry_iterator()
    for entry in reader:
        I = reader.multi_index
        original_entry = tensor.data[I[0], I[1], I[2]]
        assert(entry == 8 * original_entry)

    operator1.scale_by(amount=3.0, inplace=True)
    operator2.scale_by(amount=5.0, inplace=True)

    operator1.add(operator2, inplace=True)
    output = operator1.apply(tensor)

    reader = output.get_entry_iterator()
    for entry in reader:
        I = reader.multi_index
        original_entry = tensor.data[I[0], I[1], I[2]]
        assert(entry == 8 * original_entry)

def test_additivity_over_input_tensor():
    tolerance = 1.0 / pow(10, 9)
    random_tensors = []
    for i in range(10):
        tensor = Tensor(number_of_factors=4, dimension=2)
        writer = tensor.get_entry_iterator()
        for entry in writer:
            writer[0] = random.random()
        random_tensors.append(tensor)

    operator = TensorOperator(number_of_factors=4, dimension=2)
    writer = np.nditer(operator.data, flags = ['multi_index'], op_flags=['readwrite'])
    for entry in writer:
        writer[0] = random.random()

    for j in range(5):
        combos = combinations(random_tensors, j)
        for combo in combos:
            sum1 = Tensor(number_of_factors=4, dimension=2)
            for tensor in combo:
                sum1.add(tensor, inplace=True)
            result1 = operator.apply(sum1)

            sum2 = Tensor(number_of_factors=4, dimension=2)
            for tensor in combo:
                sum2.add(operator.apply(tensor), inplace=True)
            result2 = sum2

            assert(np.linalg.norm(result1.data - result2.data) < tolerance)

def test_additivity_over_operator():
    tolerance = 1.0 / pow(10, 9)
    random_operators = []
    for i in range(10):
        operator = TensorOperator(number_of_factors=4, dimension=2)
        writer = np.nditer(operator.data, flags = ['multi_index'], op_flags=['readwrite'])
        for entry in writer:
            writer[0] = random.random()
        random_operators.append(operator)

    tensor = Tensor(number_of_factors=4, dimension=2)
    writer = tensor.get_entry_iterator()
    for entry in writer:
        writer[0] = random.random()

    for j in range(5):
        combos = combinations(random_operators, j)
        for combo in combos:
            sum1 = TensorOperator(number_of_factors=4, dimension=2)
            for operator in combo:
                sum1.add(operator, inplace=True)
            result1 = sum1.apply(tensor)

            sum2 = TensorOperator(number_of_factors=4, dimension=2)
            for operator in combo:
                sum2.add(operator.apply(tensor), inplace=True)
            result2 = sum2

            assert(np.linalg.norm(result1.data - result2.data) < tolerance)
