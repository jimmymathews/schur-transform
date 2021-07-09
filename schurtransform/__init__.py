from .transform import SchurTransform

global_transformer = SchurTransform()

def transform(samples, **kwargs):
    """
    See ``SchurTransform.transform``.
    """
    return global_transformer.transform(samples, **kwargs)
