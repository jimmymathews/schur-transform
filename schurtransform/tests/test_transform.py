import numpy as np

import schurtransform
from schurtransform.transform import SchurTransform, SummaryType

def test_transform_norms():
    st = SchurTransform()

    samples = [
        [[4,2], [4.01,2.1], [3.9,2.2]],
        [[3.99,2.1], [3.7,2.1] ,[4.0,2.2]],
        [[4.4,1.9], [4.3,1.8], [4.3,1.8]],
        [[4.6,2.0], [4.1,1.8], [4.3,1.7]],
    ]
    decomposition = st.transform(
        samples=samples,
        summary_type=SummaryType.COMPONENTS,
    )

    samples = [
        [[1,0], [0,1], [1,1]],
        [[0,1], [-1,2], [0,1]],
    ]
    decomposition = st.transform(
        samples=samples,
        summary_type=SummaryType.COMPONENTS,
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
    number_of_samples= samples.shape[1]
    dimension = samples.shape[2]

    order = number_of_series
    projectors = t.recalculate_projectors(
        number_of_samples=number_of_samples,
        dimension=dimension,
        order=order,
    )

    centered = t.recenter_at_mean(samples)
    covariance_tensor = t.calculate_covariance_tensor(centered)
    decomposition = t.calculate_decomposition(covariance_tensor, projectors)
    assert(t.validate_decomposition(decomposition, covariance_tensor))

