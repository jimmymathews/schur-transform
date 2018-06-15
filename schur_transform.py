#!/usr/bin/python3

import numpy as np

class tensor:
    def __init__(self, n, k):
        self.n = n
        self.k = k
        self.data = np.zeros([k for i in range(n)])

    def entry_iterator_write(self):
        return np.nditer(self.data, flags = ['multi_index'], op_flags=['writeonly'])

    def entry_iterator_read(self):
        return np.nditer(self.data, flags = ['multi_index'])

class tensor_operator:
    def __init__(self, n, k):
        self.n = n
        self.k = k
        self.data = np.zeros([k for i in range(n)] + [k for i in range(n)])

    def apply(self, input_tensor):
        output_tensor = tensor(self.n, self.k)
        basis_in = input_tensor.entry_iterator_read()
        basis_out = output_tensor.entry_iterator_write()
        while not basis_out.finished:
            a_out = basis_out.multi_index

            while not basis_in.finished:
                a_in = basis_in.multi_index

            # basis_out[0] = ...

def schur_transform(x, recalculate_projectors = False):
    '''
    x is a multi-dimensional numpy array. Elements x[i,j,a].
    '''
    [n, N, k] = x.shape
    means = np.array([[np.mean(x[i,:,a]) for a in range(k)] for i in range(n)])
    for i in range(n):
        for a in range(k):
            m = means[i,a]
            for j in range(N):
                x[i,j,a] = x[i,j,a] - m

    covariance_tensor = tensor(n,k)
    it = covariance_tensor.entry_iterator_write()
    while not it.finished:
        a = it.multi_index # len(a) should equal to n, while each entry a[i] should range over k values
        it[0] = np.sum([np.prod([x[i,j,a[i]] for i in range(n)]) for j in range(N)])
        it.iternext()

x = np.array([ [[4,2,3.1],[4,2,3.2],[4,2.1,3.0]] , [[10,7.6,1.2],[10.2,7.6,1.1],[10.2,7.6,1.0]] , [[5,4,1],[5.5,4.5,1.1],[5.6,4.3,1.2]]])

schur_transform(x)