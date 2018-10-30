from distutils.core import setup

setup(
    name='RedNotebookToMarkDown',
    version='0.3dev',
    description='Utility to print RedNotebook data in the MarkDown format.',
    long_description=open('README.md').read(),
    url='http://github.com/brianrodri/RednotebookToMarkdown',
    author='Brian Rodriguez',
    author_email='brian@brianrodri.com',
    license='MIT',
    packages=['rn2md'],
    install_requires=[
        'python-dateutil',
        'defaultlist',
        'freezegun',
        'isoweek',
        'parsedatetime',
        'pyfakefs',
        'pyyaml',
    ],
)
