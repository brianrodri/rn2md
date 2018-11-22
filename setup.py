from setuptools import setup, find_packages

setup(
    name='RedNotebookToMarkDown',
    version='0.3dev',
    description='Utility to print RedNotebook data in the MarkDown format.',
    long_description=open('README.md').read(),
    author='Brian Rodriguez',
    author_email='brian@brianrodri.com',
    url='http://github.com/brianrodri/RednotebookToMarkdown',
    license=open('LICENSE').read(),
    packages=find_packages(exclude=('tests', 'docs')),
)
