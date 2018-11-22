from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='RedNotebookToMarkDown',
    version='0.3dev',
    description='Utility to print RedNotebook data in the MarkDown format.',
    long_description=open('README.md').read(),
    author='Brian Rodriguez',
    author_email='brian@brianrodri.com',
    url='http://github.com/brianrodri/RednotebookToMarkdown',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
)
