"""Setup for rn2md package."""
from setuptools import setup, find_packages

setup(
    name='rn2md',
    version='0.1.0',
    description='Utility to print RedNotebook data in Markdown format.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    license=open('LICENSE').read(),
    url='https://github.com/brianrodri/rn2md',
    author='Brian N. Rodriguez',
    author_email='brian@brianrodri.com',
    packages=find_packages(exclude=('tests',)),
    python_requires=">=3.6",
    install_requires=open('requirements.txt').read().split(),
    entry_points={
        'console_scripts': [
            'rn2md=rn2md.__main__:main',
        ],
    },
)
