Schur transform
===============

This an an implmentation of the Schur transform. This transform calculates the other tensorial components of spatial covariances and joint moments in addition to the classical, symmetric ones.

Let's say that your data are stored in multi-dimensional array `x[i,j,a]`, where

  - step index `i` ranges across `n` steps (e.g. time-steps)
  - sample index `j` ranges cross `N` samples (e.g. number of trajectories)
  - spatial index `a` ranges across `k` dimensions (e.g. 2, 3, or 4)

The following shows example usage:

```
import numpy as np
from schur_transform import schur_transform

# This example has n=4, N=3, k=3
x = np.array([ [[4,2],[4.01,2.1],[3.9,2.2]] , [[3.99,2.1],[3.7,2.1],[4.0,2.2]] , [[4.4,1.9],[4.3,1.8],[4.3,1.8]], [[4.6,2.0],[4.1,1.8],[4.3,1.7]]])
[components, amplitudes, characters] = schur_transform(x)
print("Amplitudes:  "+str(amplitudes))
print("Characters:  "+str(characters))
```

```
Calculating S4 characters.
Saved to character_tables/s4.csv
Saving projectors to projectors/dim2/steps4/*.npy
Decomposition validated to precision 1e-10.
Amplitudes:  [0.0, 0.0, 0.0001232275822899935, 0.0001926468896039451, 0.00015891651857671463]
Characters:  [[1, -1, 1, 1, -1], [3, -1, -1, 0, 1], [2, 0, 2, -1, 0], [3, 1, -1, 0, -1], [1, 1, 1, 1, 1]]
```

The `components` are the GL(k)- or Sn-isotypic components of the covariance tensor of `x` in the tensor space with `n` tensor factors and `k` dimensions for each factor. Each one is presented as a multi-dimensional numpy array with `n` indices ranging across `k` values.

**Recomputing precomputed values**. If you delete the character tables or projectors, they will be recomputed as needed. The calculation of character tables requires a local installation of Sage Math.

**Reference**.
(put reference here: *A Schur Transform for Multivariate Series*)
