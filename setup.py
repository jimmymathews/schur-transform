import setuptools
import os

dir = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(dir, 'README.rst'), 'r', encoding='utf-8') as fh:
    long_description = fh.read()

with open(os.path.join(dir, 'schurtransform', 'lung_data', 'examples_manifest.csv')) as fh:
    example_files = [row.split(',')[0] for row in fh.read().split('\n')]

requirements = [
    'numpy==1.21.0',
    'pandas==1.1.5',
]

version = '0.1.39'

setuptools.setup(
    name='schurtransform',
    version=version,
    author='James Mathews',
    author_email='mathewj2@mskcc.org',
    description='The Fourier-Schur transform for spatial statistics.',
    long_description=long_description,
    packages=[
        'schurtransform',
        'schurtransform.character_tables',
        'schurtransform.lung_data',
        'schurtransform.examples',
    ],
    package_data={
        'schurtransform': ['VERSION'],
        'schurtransform.character_tables' : [
            's2.csv',
            's3.csv',
            's4.csv',
            's5.csv',
            's6.csv',
            's7.csv',
            's8.csv',
            'symmetric_group_conjugacy_classes.csv',
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
)
