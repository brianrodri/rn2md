"""Setup for rn2md package."""
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = [l.strip() for l in f.readlines() if l.strip()]

setup(
    name='rn2md',
    version='0.1.0',
    description='Utility to print RedNotebook data in markdown format.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    license=open('LICENSE').read(),
    url='https://github.com/brianrodri/RednotebookToMarkdown',
    author='Brian N. Rodriguez',
    author_email='brian@brianrodri.com',
    packages=find_packages(exclude=('tests',)),
    python_requires=">=3.5",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'rn2md=rn2md.__main__:main',
        ],
    },
)
