from setuptools import setup

# Where the magic happens:
setup(
    name='rn2md',
    version='0.4',
    author='Brian N. Rodriguez',
    author_email='brian@brianrodri.com',
    url='https://github.com/brianrodri/RednotebookToMarkdown',
    description='Utility to translate Rednotebook data into MarkDown syntax.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license=open('LICENSE').read(),
    python_requires='>=3.7.0',
    install_requires=[
        'python-dateutil',
        'defaultlist',
        'freezegun',
        'isoweek',
        'parsedatetime',
        'pyfakefs',
        'pyyaml',
    ],
    py_modules=['rn2md'],
    entry_points={
        'console_scripts': ['rn2md=rn2md:main'],
    },
)
