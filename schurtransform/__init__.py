import importlib.resources

from .schur_transform import SchurTransform
from . import lung_data

global_transformer = SchurTransform()

with importlib.resources.path(package=lung_data, resource='examples_manifest.txt') as path:
    example_filenames = open(path).read().split('\n')

with importlib.resources.path(package=lung_data, resource=example_filenames[0]) as path:
    txt = open(path).read()

def transform(samples, **kwargs):
    """
    See ``SchurTransform.transform``.
    """
    return global_transformer.transform(samples, **kwargs)

def get_example_filenames():
    return example_filenames

def get_example_text():
    return txt
