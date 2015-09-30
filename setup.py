from setuptools import setup, find_packages
import sys, os

version = '5.67'

setup(name='arartekomaps',
      version=version,
      description="Django application serving mapak.ararteko.net ",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='maps',
      author='Gari Araolaza',
      author_email='garaolaza@codesyntax.com',
      url='https://github.com/ararteko/arartekomaps',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'cssocialuser',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
