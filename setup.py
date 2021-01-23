from setuptools import setup, find_packages
import re

def get_long_description():
    with open('README.md') as f:
        return re.sub('!\[(.*?)\]\(docs/(.*?)\)', r'![\1](https://github.com/mara/mara-mondrian/raw/master/docs/\2)', f.read())

setup(
    name='mara-mondrian',
    version='2.0.2',

    description='A python integration for the Saiku ad hoc analysis tool',

    long_description=get_long_description(),
    long_description_content_type='text/markdown',

    url = 'https://github.com/mara/mara-mondrian',

    install_requires=[
        "flask>=0.12",
        "mara-page>=1.1.0",
        "mara-schema>=1.0.0",
        "lxml>=3.8.0",
        "requests"
    ],

    python_requires='>=3.6',

    setup_requires=['setuptools_scm'],
    include_package_data=True,

    packages=find_packages(),

    author='Mara contributors',
    license='MIT',

    entry_points={},
)
