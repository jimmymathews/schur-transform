
from .schur_transform import SchurTransform

global_transformer = SchurTransform()

def transform(samples, **kwargs):
    """
    See :py:meth:`schurtransform.schur_transform.SchurTransform.transform`.
    """
    return global_transformer.transform(samples, **kwargs)
