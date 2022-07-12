import setuptools
import os
from os.path import join, dirname
import re

def get_file_contents(filename):
    package_directory = os.path.dirname(__file__)
    with open(join(package_directory, filename), 'r', encoding='utf-8') as file:
        contents = file.read()
    return contents

long_description = """[Documentation](https://schurtransform.readthedocs.io/en/stable/readme.html).
"""

example_files = get_file_contents(join('schurtransform', 'lung_data', 'examples_manifest.csv'))
example_files = [row.split(',')[0] for row in example_files.split('\n')]

requirements = [
    'numpy==1.22.3',
    'pandas==1.1.5',
    'matplotlib==3.4.2',
    'seaborn==0.11.1',
]

version = get_file_contents(join('schurtransform', 'version.txt'))

setuptools.setup(
    name='schurtransform',
    version=version,
    author='James Mathews',
    author_email='mathewj2@mskcc.org',
    description='The Fourier-Schur transform for spatial statistics.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    scripts=[
        'scripts/schurtransform-calculate-projectors',
        'scripts/regenerate-symmetric-group-characters',
    ],
    packages=[
        'schurtransform',
        'schurtransform.character_tables',
        'schurtransform.projectors',
        'schurtransform.lung_data',
        'schurtransform.examples',
    ],
    package_data={
        'schurtransform': ['version.txt'],
        'schurtransform.character_tables' : [
            's2.csv',
            's3.csv',
            's4.csv',
            's5.csv',
            's6.csv',
            'symmetric_group_conjugacy_classes.csv',
        ],
        'schurtransform.projectors' : [
            'projectors_degree_2_dimension_2.npz',
            'projectors_degree_3_dimension_2.npz',
            'projectors_degree_4_dimension_2.npz',
            'projectors_degree_5_dimension_2.npz',
            'projectors_degree_6_dimension_2.npz',
            'projectors_degree_2_dimension_3.npz',
            'projectors_degree_3_dimension_3.npz',
            'projectors_degree_4_dimension_3.npz',
            'projectors_degree_5_dimension_3.npz',
            'projectors_degree_6_dimension_3.npz',
        ],
        'schurtransform.lung_data' : example_files + ['examples_manifest.csv'],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Scientific/Engineering',
        'Intended Audience :: Science/Research',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    project_urls = {
        'Documentation': 'https://schurtransform.readthedocs.io/en/stable/readme.html',
        'Source code': 'https://github.com/schur-transform/schurtransform'
    },
    url = 'https://github.com/schur-transform/schurtransform',
)
