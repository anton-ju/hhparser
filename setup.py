from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='pypokertools',
    version='0.4.3',
    packages=find_packages(),
    install_requires=['beautifulsoup4==4.7.1',
                      'numpy==1.16.2',
                      ],
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
)
