import importlib
import importlib.resources

from .transform import SchurTransform
# from . import lung_data

global_transformer = SchurTransform()

def transform(samples, **kwargs):
    """
    See ``SchurTransform.transform``.
    """
    return global_transformer.transform(samples, **kwargs)


# with importlib.resources.path(lung_data, 'examples_manifest.txt') as path:
#     example_filenames = open(path).read().split('\n')

# with importlib.resources.path(lung_data, example_filenames[0]) as path:
#     txt = open(path).read()

# def get_example_filenames():
#     return example_filenames

# def get_example_text():
#     return txt
