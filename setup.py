from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Crypto Technical Analysis'
LONG_DESCRIPTION = 'Combines a few packages to perform Technical Analysis for Cryptocurrencies.'

with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    requirements = [l for l in requirements if not l.startswith('#')]

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="crypto_ta", 
        version=VERSION,
        author="dokato",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(include=['crypto_ta', 'crypto_ta.*']),
        url='https://github.com/dokato',
        keywords=['python', 'cryptocurrencies', 'technical analysis'],
        classifiers= [
            'Development Status :: 3 - Alpha',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9'
        ],
        install_requires=requirements,
        python_requires='>=3.6'
)

