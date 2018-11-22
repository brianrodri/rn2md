from setuptools import setup

setup(
    name='rn2md',
    version='0.4dev',
    description='Utility to print RedNotebook data in the MarkDown format.',
    long_description=open('README.md').read(),
    author='Brian Rodriguez',
    author_email='brian@brianrodri.com',
    url='http://github.com/brianrodri/RednotebookToMarkdown',
    license=open('LICENSE').read(),
    packages=['rn2md'],
    entry_points={
        'console_scripts': [
            'rn2md = rn2md.__main__:main'
        ]
    },
)
