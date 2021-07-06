import setuptools
import os

dir = os.path.dirname(__file__)

with open(os.path.join(dir, 'README.md'), 'r', encoding='utf-8') as fh:
    long_description = fh.read()

with open(os.path.join(dir, 'requirements.txt'), 'r', encoding='utf-8') as fh:
    requirements = fh.read().split('\n')

with open(os.path.join(dir, 'VERSION')) as fh:
    version = fh.read().rstrip('\n')

setuptools.setup(
    name='schurtransform',
    version=version,
    author='James Mathews',
    author_email='mathewj2@mskcc.org',
    description='The Fourier-Schur transform for spatial statistics.',
    long_description=long_description,
    packages=[
        'schurtransform',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    package_data={'schurtransform': ['VERSION']},
    python_requires='>=3.8',
    install_requires=requirements,
)
