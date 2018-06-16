#!/usr/bin/python3

import numpy as np
from subprocess import call
import math
import os
import csv
import re

class tensor:
    def __init__(self, n, k):
        self.n = n
        self.k = k
        self.data = np.zeros([k for i in range(n)])

    def entry_iterator_write(self):
        return np.nditer(self.data, flags = ['multi_index'], op_flags=['writeonly'])

    def entry_iterator_read(self):
        return np.nditer(self.data, flags = ['multi_index'])

    def add(self, other_tensor):
        if(self.data.shape != other_tensor.data.shape):
            print("Error, shapes "+str(self.data.shape) + " and "+str(other_tensor.data.shape)+ " do not agree.")
        else:
            self.data = self.data + other_tensor.data

class tensor_operator:
    def __init__(self, n, k, identity=False, permutation_inverse=None):
        self.n = n
        self.k = k
        self.data = np.zeros([k for i in range(n)] + [k for i in range(n)])
        if(identity):
            it = np.nditer(self.data, flags = ['multi_index'])
            while not it.finished:
                index = it.multi_index
                in_index = [index[i] for i in range(n)]
                out_index = [index[i+n] for i in range(n)]

                if(in_index == out_index):
                    self.data[index] = 1.0
                it.iternext()

        if(permutation_inverse != None):
            it = np.nditer(self.data, flags = ['multi_index'])
            while not it.finished:
                index = it.multi_index
                in_index = [index[i] for i in range(n)]
                out_index = [index[i+n] for i in range(n)]

                permuted_in_index = [index[permutation_inverse[i]-1] for i in range(n)]  # The -1 is for converting to 0-based indexing.
                if(permuted_in_index == out_index):
                    self.data[index] = 1.0
                it.iternext()

    def apply(self, input_tensor):
        output_tensor = tensor(self.n, self.k)
        component_out = output_tensor.entry_iterator_write()
        while not component_out.finished:
            a_out = component_out.multi_index
            component_in = input_tensor.entry_iterator_read()
            while not component_in.finished:
                a_in = component_in.multi_index
                component_out[0] = component_out[0] + self.data[a_out + a_in] * component_in[0]
                component_in.iternext()
            component_out.iternext()
        return output_tensor

    def add(self, other_operator):
        self.data = self.data + other_operator.data

    def scale_by(self, amount):
        to = tensor_operator(self.n, self.k)
        to.data = self.data * amount
        return to

def load_table(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        all_rows = []
        for row in reader:
            all_rows.append(row)

    sizes_str = all_rows[0]
    sizes = [int(val) for val in sizes_str]
    characters_str = all_rows[2:]
    character_values = [[int(val) for val in row] for row in characters_str]
    return [sizes, all_rows[1], character_values]

def partition_from_cycle_type(cycle_type, n):
    cycles = re.findall("\\(([\s\d]+)\\)", cycle_type)
    if(len(cycles)<1):
        return [1 for i in range(n)]

    partition = []
    for cycle in cycles:
        numbers = re.findall("(\d+)", cycle)
        partition.append(len(numbers))

    return sorted(partition + [1 for w in range(n-sum(partition))])

def first_zero(mask):
    for i in range(len(mask)):
        if(mask[i] == 0):
            return i
    return -1

def partition_from_permutation(permutation):
    n = len(permutation)
    masked = [0 for i in range(n)]

    descriptor = "( "

    cycle_start = 0
    descriptor = descriptor + str(permutation[cycle_start])+" "
    masked[cycle_start] = 1
    next_index = permutation[cycle_start]-1
    cycle_lengths = []
    cycle_length = 1
    while(sum(masked) < n):
        if(next_index == cycle_start):
            descriptor = descriptor + ")( "
            cycle_lengths.append(cycle_length)
            cycle_length = 1
            cycle_start = first_zero(masked)
            descriptor = descriptor + str(permutation[cycle_start]) + " "
            masked[cycle_start] = 1
            next_index = permutation[cycle_start]-1
            continue
        else:
            descriptor = descriptor + str(permutation[next_index])+" "
            masked[next_index] = 1
            next_index = permutation[next_index]-1
            cycle_length = cycle_length + 1
            if(sum(masked)==n):
                break
    cycle_lengths.append(cycle_length)
    descriptor = descriptor + ")"
    return sorted(cycle_lengths)

def partitions_compared(l1, l2):
    return (sorted(l1) == sorted(l2))

def list_permutations_by_conjugacy_class(classes, sizes, n):
    permutations_by_class = [[] for cc in classes]

    import itertools
    permutations = list(itertools.permutations([i+1 for i in range(n)]))
    for permutation in permutations:
        partition = partition_from_permutation(permutation)
        for i in range(len(classes)):
            if(partitions_compared(partition, classes[i])):
                permutations_by_class[i].append(permutation)

    for i,c in enumerate(permutations_by_class):
        if(len(c)!=sizes[i]):
            print("Error: Found "+ str(len(c))+" permutations of certain class, not "+str(sizes[i])+".")
    return permutations_by_class

def schur_transform(x):
    '''
    x is a multi-dimensional numpy array. Elements x[i,j,a].
    '''
    [n, N, k] = x.shape

    with open("generate_character_tables_config.py", "w") as file:
        file.write("current_n="+str(n)+"\n")
    if(not os.path.isfile("character_tables/s"+str(n)+".csv")):
        call(["sage", "generate_character_tables.sage"])
    if(os.path.isfile("generate_character_tables.sage.py")):
        call(["rm", "generate_character_tables.sage.py"])
    call(["rm", "generate_character_tables_config.py"])

    [conjugacy_class_sizes, conjugacy_class_representatives, character_values] = load_table("character_tables/s"+str(n)+".csv")

    # print(conjugacy_class_sizes)
    # print(conjugacy_class_representatives)
    # print(character_values)

    if(not os.path.isfile("projectors/dim"+str(k)+"/steps"+str(n)+"/0.npy")):
        print("Saving projectors to projectors/dim"+str(k)+"/steps"+str(n)+"/*.npy")
        ps = [partition_from_cycle_type(repstr, n) for repstr in conjugacy_class_representatives]
        classes = list_permutations_by_conjugacy_class(ps, conjugacy_class_sizes, n)

        collated_permutation_operators = []
        for cc in classes:
            # add together linear representation of all the permutations in the class cc. scale appropriately, and save as npy file.
            collated = tensor_operator(n, k)
            for permutation in cc:
                collated.add(tensor_operator(n, k, permutation_inverse = permutation))
            collated_permutation_operators.append(collated)

        for l, character in enumerate(character_values):
            projector = tensor_operator(n, k)
            for m, collated in enumerate(collated_permutation_operators):
                projector.add(collated.scale_by(character[m]))
            projector = projector.scale_by(character[0]/math.factorial(n))

            if(not os.path.exists("projectors/")):
                os.makedirs("projectors/")
            if(not os.path.exists("projectors/dim"+str(k)+"/")):
                os.makedirs("projectors/dim"+str(k)+"/")
            if(not os.path.exists("projectors/dim"+str(k)+"/steps"+str(n)+"/")):
                os.makedirs("projectors/dim"+str(k)+"/steps"+str(n)+"/")

            fn = "projectors/dim"+str(k)+"/steps"+str(n)+"/"+str(l)+".npy"
            np.save(fn, projector.data)

    means = np.array([[np.mean(x[i,:,a]) for a in range(k)] for i in range(n)])
    for i in range(n):
        for a in range(k):
            m = means[i,a]
            for j in range(N):
                x[i,j,a] = x[i,j,a] - m

    covariance_tensor = tensor(n, k)
    it = covariance_tensor.entry_iterator_write()
    while not it.finished:
        a = it.multi_index # len(a) should equal to n, while each entry a[i] should range over k values
        it[0] = np.sum([np.prod([x[i,j,a[i]] for i in range(n)]) for j in range(N)])
        it.iternext()

    decomposition = []
    for l, character in enumerate(character_values):
        file = "projectors/dim"+str(k)+"/steps"+str(n)+"/"+str(l)+".npy"
        pickled= np.load(file)
        projector = tensor_operator(n, k)
        projector.data = pickled
        component = projector.apply(covariance_tensor)
        decomposition.append(component)

    # Validation of decomposition
    total = tensor(n, k)
    for component in decomposition:
        total.add(component)
    error = np.linalg.norm(total.data - covariance_tensor.data)
    precision = 0.0000000001
    if(error > precision):
        print("Error: Components do not add up to given covariance tensor. ("+str(error)+")")
    else:
        print("Decomposition validated to precision "+str(precision)+".")

    amplitudes = [np.linalg.norm(component.data) for component in decomposition]
    return [[component.data for component in decomposition], amplitudes, character_values]
