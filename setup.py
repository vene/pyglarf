import pyglarf
from distutils.core import setup

CLASSIFIERS = """\
Development Status :: 3 - Alpha
Intended Audience :: Science/Research
License :: OSI Approved :: BSD License
Programming Language :: Python
Topic :: Software Development
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS
Operating System :: Microsoft :: Windows

"""

setup(
    name='pyglarf',
    description='Python utilities for working on top of GLARF\'s output.',
    long_description=open('README.md').read(),
    version=pyglarf.__version__,
    author='Vlad Niculae',
    author_email='vlad@vene.ro',
    packages=['pyglarf'],
    classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],

)
