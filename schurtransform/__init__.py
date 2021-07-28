
from .schur_transform import SchurTransform
from .examples import get_example_data
from .plotting import create_figure

global_transformer = SchurTransform()

def transform(samples, **kwargs):
    """
    See :py:meth:`.schur_transform.SchurTransform.transform`.
    """
    return global_transformer.transform(samples, **kwargs)

