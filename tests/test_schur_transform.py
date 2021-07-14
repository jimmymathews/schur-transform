import numpy as np

import schurtransform as st
from schurtransform.schur_transform import SchurTransform

def test_transform_norms():
    samples = [
        [[4,2], [4.01,2.1], [3.9,2.2]],
        [[3.99,2.1], [3.7,2.1] ,[4.0,2.2]],
        [[4.4,1.9], [4.3,1.8], [4.3,1.8]],
        [[4.6,2.0], [4.1,1.8], [4.3,1.7]],
    ]
    decomposition = st.transform(
        samples=samples,
    )

    samples = [
        [[1,0], [0,1], [1,1]],
        [[0,1], [-1,2], [0,1]],
    ]
    decomposition = st.transform(
        samples=samples,
    )

def test_decomposition_recomposition():
    t = SchurTransform()
    samples = [
        [[4,2], [4.01,2.1], [3.9,2.2]],
        [[3.99,2.1], [3.7,2.1] ,[4.0,2.2]],
        [[4.4,1.9], [4.3,1.8], [4.3,1.8]],
        [[4.6,2.0], [4.1,1.8], [4.3,1.7]],
        [[3.6,2.1], [4.5,2], [5,1]],
        [[3.0,2.2], [7,2.2], [5.6,1.2]],
    ]

    if type(samples) is list:
        samples = np.array(samples)

    number_of_series = samples.shape[0]
    dimension = samples.shape[2]

    degree = number_of_series
    projectors = t.recalculate_projectors(
        dimension=dimension,
        degree=degree,
    )

    centered = t.recenter_at_mean(samples)
    covariance_tensor = t.calculate_covariance_tensor(centered)
    decomposition = t.calculate_decomposition(covariance_tensor, projectors)
    assert(t.validate_decomposition(decomposition, covariance_tensor))

def test_content():
    samples = [
        [[4,2], [4.01,2.1], [3.9,2.2]],
        [[3.99,2.1], [3.7,2.1] ,[4.0,2.2]],
        [[4.4,1.9], [4.3,1.8], [4.3,1.8]],
        [[4.6,2.0], [4.1,1.8], [4.3,1.7]],
        [[3.6,2.1], [4.5,2], [5,1]],
        [[3.0,2.2], [7,2.2], [5.6,1.2]],
    ]
    content = st.transform(
        samples=samples,
        summary='CONTENT',
    )



