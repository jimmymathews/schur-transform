import importlib.resources

from .schur_transform import SchurTransform
from . import lung_data

global_transformer = SchurTransform()

with importlib.resources.path(package=lung_data, resource='examples_manifest.txt') as path:
    example_filenames = open(path).read().split('\n')

def transform(samples, **kwargs):
    """
    See :py:meth:`schurtransform.schur_transform.SchurTransform.transform`.
    """
    return global_transformer.transform(samples, **kwargs)

def get_example_filenames():
    return example_filenames
