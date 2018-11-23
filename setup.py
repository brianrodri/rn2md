"""Setup for rn2md package."""
from setuptools import setup, find_packages

setup(
    name='rn2md',
    version='0.1.0',
    description='Utility to print RedNotebook data in markdown format',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    license=open('LICENSE').read(),
    url='https://github.com/brianrodri/RednotebookToMarkdown',
    author='Brian N. Rodriguez',
    author_email='brian@brianrodri.com',
    packages=find_packages(exclude=('tests',)),
    install_requires=[
        'defaultlist',
        'freezegun',
        'isoweek',
        'parsedatetime',
        'pyfakefs',
        'python-dateutil',
        'pyyaml',
    ],
    extras_require={
        dev: ['pylint'],
    },
    entry_points={
        'console_scripts': [
            'rn2md=rn2md.__main__:main',
        ],
    },
)
