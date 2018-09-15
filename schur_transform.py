#!/usr/bin/python3

import numpy as np
from subprocess import call
import math
import os
import csv
import re

class tensor:
    '''
    A data structure for a tensor of type V⊗...⊗V.
    '''
    def __init__(self, n, k):
        '''
        n is the number of factors.
        k is the dimension of the base vector space.
        '''
        self.n = n
        self.k = k
        self.data = np.zeros([k for i in range(n)])

    def entry_iterator_write(self):
        '''
        Since the number of tensor factors might be large, it will rarely be convenient enough to write nested for loops to iterate over the components of the tensor, so this iterator is provided.
        Note that the flags ensure that
            the_iterator.multi_index
        will return a tuple consisting of the indices of the currently-selected component or entry.
        The currently-selected entry is set with
            the_iterator = new_value
        For sample usage of the iterator, see tensor_operator.apply.
        '''
        return np.nditer(self.data, flags = ['multi_index'], op_flags=['writeonly'])

    def entry_iterator_read(self):
        '''
        Since the number of tensor factors might be large, it will rarely be convenient enough to write nested for loops to iterate over the components of the tensor, so this iterator is provided.
        Note that the flags ensure that
            the_iterator.multi_index
        will return a tuple consisting of the indices of the currently-selected component or entry.
        '''
        return np.nditer(self.data, flags = ['multi_index'])

    def add(self, other_tensor):
        '''
        In-place addition of another tensor.
        '''
        if(self.data.shape != other_tensor.data.shape):
            print("Error, shapes "+str(self.data.shape) + " and "+str(other_tensor.data.shape)+ " do not agree.")
        else:
            self.data = self.data + other_tensor.data

    def scale_by(self, amount):
        '''
        Returns new tensor scaled entry by entry by amount.
        '''
        t = tensor(self.n, self.k)
        t.data = self.data * amount
        return t

class tensor_operator:
    '''
    A data structure for an endomorphism of tensors, a linear transformation, an element of End(V⊗...⊗V).
    '''
    def __init__(self, n, k, identity = False, permutation_inverse = None):
        '''
        n is the number of tensor factors.
        k is the dimension for the base vector space.
        identity = True will make this tensor_operator into the identity operator.
        permutation_inverse = p will make this tensor_operator into the operator of permutation of the n tensor factors. p should be formatted as in [1, 2, 3].
        '''
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
        '''
        Just application of this tensor_operator as a linear map to the input tensor.
        '''
        if(input_tensor.n != self.n or input_tensor.k != self.k):
            print("Error: input_tensor type (n,k)=("+str(input_tensor.n)+","+str(input_tensor.k)+") is wrong.")
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


class SymmetricGroupUtilities:
    '''
    Has helper functions for working with permutations and their characters.
    '''
    def read_csv_values_raw_list(self, filename):
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            all_rows = []
            for row in reader:
                all_rows.append(row)
        return all_rows

    def load_character_table(self, filename):
        '''
        Loads character table as saved by generate_character_tables.sage, for use in generating the projectors.
        The first row is conjugacy class cardinalities. The second row is example members of each conjugacy class, in cycle notation. The third row and beyond are the character values, one row for each character.
        This assumes the usage of the symmetric group in the sense that it assumes integral values for the characters.
        '''
        values = self.read_csv_values_raw_list(filename)
        sizes_str = values[0]
        sizes = [int(val) for val in sizes_str]
        characters_str = values[2:]
        character_numeric = [[int(val) for val in row] for row in characters_str]
        return [sizes, values[1], character_numeric]

    def partition_from_cycle_type(self, cycle_type, n):
        '''
        Returns an ordered list of integers which partition the integer n, representing the cycle type specified by the string cycle_type. The format of cycle_type should be as in (1 2)(3 4). The parenthesis are mandatory, and the spacing is somewhat optional in that other characters may be used as spacers as long as they are non-digits. The cycle lengths are calculated as the number of contiguous digit groups between parentheses.
        '''
        cycles = re.findall("\\(([\s\d]+)\\)", cycle_type)
        if(len(cycles)<1):
            return [1 for i in range(n)]

        partition = []
        for cycle in cycles:
            numbers = re.findall("(\d+)", cycle)
            partition.append(len(numbers))

        return sorted(partition + [1 for w in range(n-sum(partition))])

    def first_zero(self, mask):
        '''
        Utility function finding the index of the first zero entry of mask.
        '''
        for i in range(len(mask)):
            if(mask[i] == 0):
                return i
        return -1

    def partition_from_permutation(self, permutation):
        '''
        Returns an ordered list of integers which partition the integer n, representing the cycle type of the argument permutation. The format of permutation should be a list as in [1 ,2 ,3].
        Also builds a cycle-notation string description of the permutation (not returned).
        '''
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
                cycle_start = self.first_zero(masked)
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
        # print(descriptor)
        return sorted(cycle_lengths)

    def partitions_compared(self, l1, l2):
        '''
        Tests equality of partitions. Used to check common membership in a conjugacy class of the symmetric group.
        '''
        return (sorted(l1) == sorted(l2))

    def list_permutations_by_conjugacy_class(self, classes, sizes, n):
        '''
        The very inefficient intermediate step of the algorithm used by this implementation.
        It enumerates all permutations then sorts them into Sn conjugacy class bins by testing each one for cycle type. It returns a list of lists of permutations, in the same order as the set of conjugacy classes listed in the argument classes.
        Each element of classes should be a partition of n representing a conjugacy class in Sn.
        As a verification step, it checks that the number of permutations in each bin matches the cardinality specified in the argument sizes.
        '''
        permutations_by_class = [[] for cc in classes]

        import itertools
        permutations = list(itertools.permutations([i+1 for i in range(n)]))
        for permutation in permutations:
            partition = self.partition_from_permutation(permutation)
            for i in range(len(classes)):
                if(self.partitions_compared(partition, classes[i])):
                    permutations_by_class[i].append(permutation)

        for i,c in enumerate(permutations_by_class):
            if(len(c)!=sizes[i]):
                print("Error: Found "+ str(len(c))+" permutations of certain class, not "+str(sizes[i])+".")
        return permutations_by_class

class DiscreteSchurTransform():
    def __init__(self, x):
        '''
        x should be in the format of numpy ndarray x[i,j,a]. i is the series index, j is the sample index, and a is the spatial coordinate index.
        For the future: Allow x to be a list of such ndarrays, for batch processing.
        '''
        self.x = x
        [self.n, self.N, self.k] = x.shape
        self.precomputations()
        self.main_computation()

    def precomputations(self):
        self.consider_generate_and_load_character_table()
        self.consider_generate_and_load_projectors()

    def main_computation(self):
        self.calculate_means()
        self.calculate_covariance_tensor()
        self.calculate_decomposition()
        self.validate_decomposition()

    def summary(self):
        amplitudes = [np.linalg.norm(component.data) for component in self.decomposition]
        return [[component.data for component in self.decomposition], amplitudes, self.character_values]

    def consider_generate_and_load_character_table(self):
        '''
        Checks if character table of Sn is already calculated. If not, regenerate. Requires Sage Math.
        '''
        with open("generate_character_tables_config.py", "w") as file:
            file.write("current_n="+str(self.n)+"\n")
        if(not os.path.isfile("character_tables/s"+str(self.n)+".csv")):
            print("Firing up Sage.")
            call(["sage", "generate_character_tables.sage"])
        if(os.path.isfile("generate_character_tables.sage.py")):
            call(["rm", "generate_character_tables.sage.py"])
        call(["rm", "generate_character_tables_config.py"])

        self.sgu = SymmetricGroupUtilities()
        [self.conjugacy_class_sizes, self.conjugacy_class_representatives, self.character_values] = self.sgu.load_character_table("character_tables/s"+str(self.n)+".csv")

    def consider_generate_and_load_projectors(self):
        '''
        Checks if the projectors for given number of tensor factors n and spatial dimension k are calculated. If not, regenerate.
        '''
        if(os.path.isfile("projectors/dim"+str(self.k)+"/steps"+str(self.n)+"/0.npy")):
            return
        print("Calculating projectors.")
        ps = [self.sgu.partition_from_cycle_type(repstr, self.n) for repstr in self.conjugacy_class_representatives]
        classes = self.sgu.list_permutations_by_conjugacy_class(ps, self.conjugacy_class_sizes, self.n)

        collated_permutation_operators = []
        for cc in classes:
            # Add together linear representation of all the permutations in the class cc. Save as npy binary file.
            collated_permutation_operator = tensor_operator(self.n, self.k)
            for permutation in cc:
                collated_permutation_operator.add(tensor_operator(self.n, self.k, permutation_inverse = permutation))
            collated_permutation_operators.append(collated_permutation_operator)

        for l, character in enumerate(self.character_values):
            # Convolves with character.
            projector = tensor_operator(self.n, self.k)
            for m, collated_permutation_operator in enumerate(collated_permutation_operators):
                projector.add(collated_permutation_operator.scale_by(character[m]))
            # These projectors are scaled by factorial(n). Neglecting to normalize them at this stage allows integral values and greater precision.
            projector = projector.scale_by(character[0])

            if(not os.path.exists("projectors/")):
                os.makedirs("projectors/")
            if(not os.path.exists("projectors/dim"+str(self.k)+"/")):
                os.makedirs("projectors/dim"+str(self.k)+"/")
            if(not os.path.exists("projectors/dim"+str(self.k)+"/steps"+str(self.n)+"/")):
                os.makedirs("projectors/dim"+str(self.k)+"/steps"+str(self.n)+"/")

            fn = "projectors/dim"+str(self.k)+"/steps"+str(self.n)+"/"+str(l)+".npy"
            np.save(fn, projector.data)
        self.validate_projectors_decomposition()
        print("Saved projectors to projectors/dim"+str(self.k)+"/steps"+str(self.n)+"/*.npy")

    def validate_projectors_decomposition(self):
        sum_of_projectors = tensor_operator(self.n, self.k)
        for l, character in enumerate(self.character_values):
            file = "projectors/dim"+str(self.k)+"/steps"+str(self.n)+"/"+str(l)+".npy"
            projector = tensor_operator(self.n, self.k)
            pickled= np.load(file)
            projector.data = pickled
            sum_of_projectors.add(projector)

        identity_scaled = tensor_operator(self.n, self.k, identity = True).scale_by(math.factorial(self.n))
        if(not (sum_of_projectors.data==identity_scaled.data).all() ):
            print("Error: Projectors do not sum to identity.")
        else:
            print("Projectors sum to identity operator.")

    def calculate_means(self):
        self.means = np.array([[np.mean(self.x[i,:,a]) for a in range(self.k)] for i in range(self.n)])
        for i in range(self.n):
            for a in range(self.k):
                m = self.means[i,a]
                for j in range(self.N):
                    self.x[i,j,a] = self.x[i,j,a] - m

    def calculate_covariance_tensor(self):
        self.covariance_tensor = tensor(self.n, self.k)
        it = self.covariance_tensor.entry_iterator_write()
        while not it.finished:
            a = it.multi_index # len(a) should equal to n, while each entry a[i] should range over k values
            it[0] = np.sum([np.prod([self.x[i,j,a[i]] for i in range(self.n)]) for j in range(self.N)])
            it.iternext()

    def calculate_decomposition(self):
        self.decomposition = []
        for l, character in enumerate(self.character_values):
            file = "projectors/dim"+str(self.k)+"/steps"+str(self.n)+"/"+str(l)+".npy"
            projector = tensor_operator(self.n, self.k)
            pickled= np.load(file)
            # print(" ".join([str(val) for val in pickled.flatten()]))
            projector.data = pickled
            component = projector.apply(self.covariance_tensor)
            self.decomposition.append(component.scale_by(1.0/math.factorial(self.n)))

    def validate_decomposition(self):
        '''
        Checks that the sum of the components of the decomposition is the original covariance tensor.
        '''
        total = tensor(self.n, self.k)
        for component in self.decomposition:
            total.add(component)
        error = np.linalg.norm(total.data - self.covariance_tensor.data)
        precision = 0.0000000001
        if(error > precision):
            print("Error: Components do not add up to given covariance tensor. (Difference norm "+str(error)+")")

def dst(x):
    '''
    Calculates the (discrete) Schur transform of x.
    x is a multi-dimensional numpy array. Elements x[i,j,a], where
    i is the series index,
    j is the sample index, and
    a is the spatial dimension index.
    '''
    dst = DiscreteSchurTransform(x)
    return dst.summary()

