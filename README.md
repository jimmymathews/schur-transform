schurtransform
==============

Fourier-Schur analysis is an analogue of Fourier analysis in which the time domain and corresponding cyclic symmetry are replaced by the spatial joint moment tensor domain and permutation symmetry. It is used to derive natural higher-order statistics for "registered" spatial datasets.

This repository contains an implementation of the algorithm described in [*A Schur Transform for Spatial Stochastic Processes*](https://arxiv.org/abs/1811.06221). The transform calculates irreducible tensorial components of spatial joint moments and their amplitudes. See also Persi Diaconis' [Group Representations in Probability and Statistics](https://www.jstor.org/stable/4355560) for background on the non-abelian Fourier transform in the context of the symmetric group.

Let's say that your data are stored in a multi-dimensional array `v[i,j,a]` (or similar list-of-list-of-lists), where

  - step index `i` ranges across `n` steps (e.g. time-steps, or random variables)
  - sample index `j` ranges cross `N` samples (e.g. number of trajectories or landmarks)
  - spatial index `a` ranges across `k` dimensions (e.g. `k=3`)

The following shows example usage:

```python
import schurtransform as st
samples = [
    [[4,2], [4.01,2.1], [3.9,2.2]],
    [[3.99,2.1], [3.7,2.1] ,[4.0,2.2]],
    [[4.4,1.9], [4.3,1.8], [4.3,1.8]],
    [[4.6,2.0], [4.1,1.8], [4.3,1.7]],
]
decomposition = st.transform(
    samples=samples,
)

decomposition['3+1'].data

>>  array([[[[ 0.00000000e+00,  4.44722222e-05],
>>           [ 3.48055556e-05, -3.82222222e-05]],
>>
>>          [[ 2.09166667e-05,  6.05555556e-05],
>>           [ 1.22222222e-05, -4.38888889e-05]]],
>>
>>
>>         [[[-1.00194444e-04, -1.22222222e-05],
>>           [-6.05555556e-05, -6.83333333e-05]],
>>
>>          [[ 3.82222222e-05,  5.61111111e-05],
>>           [ 5.61111111e-05,  0.00000000e+00]]]])
```

The `components` are the GL(k)- or Sn-isotypic components of the covariance tensor of `v` in the tensor space with `n` tensor factors and `k` dimensions for each factor. Each one is presented as a multi-dimensional numpy array with `n` indices ranging across `k` values.

**Recomputing precomputed values**. If you delete the character tables or projectors, they will be recomputed as needed. The calculation of character tables requires a local installation of Sage Math.

**Demo**. *demo.py* is a more extensive usage example. It calculates the *Schur content* (many Schur transforms for various subsets of the series index) of a lung deformation as measured by a 4D CT scan. Data available for download from [DIR-lab](https://dir-lab.com). Requires the Seaborn Python library (for violin plots) and Pandas.

![alttext](combo_dirlab_sc.png)
