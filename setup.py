import setuptools
import os

dir = os.path.dirname(__file__)

with open(os.path.join(dir, 'README.md'), 'r', encoding='utf-8') as fh:
    long_description = fh.read()

with open(os.path.join(dir, 'requirements.txt'), 'r', encoding='utf-8') as fh:
    requirements = fh.read().split('\n')

with open(os.path.join(dir, 'VERSION')) as fh:
    version = fh.read().rstrip('\n')

with open(os.path.join(dir, 'schurtransform', 'lung_data', 'examples_manifest.txt')) as fh:
    example_files = fh.read().split('\n')

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
    ],
    package_data={
        'schurtransform': ['VERSION'],
        'schurtransform.character_tables' : ['s2.csv', 's3.csv', 's4.csv', 's5.csv', 's6.csv', 's7.csv', 's8.csv', 'symmetric_group_conjugacy_classes.csv'],
        'schurtransform.lung_data' : example_files + ['examples_manifest.txt'],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
)
