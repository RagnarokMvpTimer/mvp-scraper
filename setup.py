from setuptools import setup, find_packages

from mvp_scraper import __author__, __version__, __email__

with open('requirements.txt') as r:
  requirements = r.readlines()

with open('README.md', encoding='utf-8') as ld:
  long_description = ld.read()

setup(
  name='mvp-scraper',
  version=__version__,
  packages=find_packages(),
  url='https://github.com/RagnarokMvpTimer/mvp-scraper',
  license='MIT',
  author=__author__,
  author_email=__email__,
  description='',
  long_description=long_description,
  long_description_content_type="text/markdown",
  install_requires=requirements,
  include_package_data=True,
  zip_safe=False,
  python_requires='>=3.8',
  classifiers=[
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Topic :: Terminals',
    'Topic :: Utilities',
  ],
)
