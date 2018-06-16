Schur transform
===============

Usage
-----

Assume that data are stored in numpy array `x[i,j,a]`, where

  - step index `i` ranges across `n` steps (e.g. time-steps)
  - sample index `j` ranges cross `N` samples (e.g. number of trajectories)
  - spatial index `a` ranges across `k` dimensions

```
import numpy as np
from schur_transform.py import schur_transform

x = np.array([ [[4,2],[4.01,2.1],[3.9,2.2]] , [[3.99,2.1],[3.7,2.1],[4.0,2.2]] , [[4.4,1.9],[4.3,1.8],[4.3,1.8]], [[4.6,2.0],[4.1,1.8],[4.3,1.7]]])
[components, amplitudes, characters] = schur_transform(x)
print("Amplitudes:  "+str(amplitudes))
print("Characters:  "+str(characters))
```

```

```

Recomputing precomputed values
------------------------------

To recompute the character tables or projectors, delete them. They will be recomputed as needed.

The calculation of character tables requires a local installation of SageMath.