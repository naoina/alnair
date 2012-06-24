import os

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class pytest(TestCommand):
    def initialize_options(self):
        TestCommand.initialize_options(self)

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_suite = True
        self.test_args = ['tests']

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        raise SystemExit(pytest.main(self.test_args))

version = '0.1'

install_requires = [
    'fabric>=1.4.2',
    ]

tests_require = [
    'mock',
    'pytest-quickcheck',
    'pytest',
    ]

here = os.path.abspath(os.path.dirname(__file__))

README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

setup(name='alnair',
      version=version,
      description="A simple system integration framework",
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2',
          'Topic :: Software Development :: Build Tools'
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Installation/Setup',
          'Topic :: System :: Software Distribution'
          'Topic :: System :: Systems Administration',
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Naoya Inada',
      author_email='naoina@kuune.org',
      url='https://github.com/naoina/alnair',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      entry_points="""
      # -*- Entry points: -*-
      """,
      cmdclass = {'test': pytest},
      )
