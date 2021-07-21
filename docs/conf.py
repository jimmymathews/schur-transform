# -*- coding: utf-8 -*-

# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../'))

# -- Project information -----------------------------------------------------
project = 'schurtransform'
copyright = '2021, James Mathews'
author = 'James Mathews'

# The short X.Y version
# version = ''
# The full version, including alpha/beta/rc tags
release = '0.1.47'

# -- General configuration ---------------------------------------------------
needs_sphinx = '1.8.5'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
import sphinx_rtd_theme
extensions = [
    'sphinx.ext.autodoc',
    'sphinx_rtd_theme',
    'sphinx.ext.napoleon',
    'sphinx.ext.imgmath',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

source_suffix = '.rst'
master_doc = 'index'
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = None
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

htmlhelp_basename = 'schurtransformdoc'

# -- Extension configuration -------------------------------------------------
add_module_names = False
autodoc_default_flags = [
    'members',
    'undoc-members',
    'private-members',
    'inherited-members',
    'show-inheritance',
]

autoclass_content = 'both'
