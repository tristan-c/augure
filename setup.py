#!/usr/bin/env python
# coding: utf-8

import os
import sys
import re

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

if sys.version < '3':
  import codecs
  def u(x):
    return codecs.unicode_escape_decode(x)[0]
else:
  def u(x):
    return x

def get_version():
    VERSIONFILE = 'augure/__init__.py'
    initfile_lines = open(VERSIONFILE, 'rt').readlines()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    for line in initfile_lines:
        mo = re.search(VSRE, line, re.M)
        if mo:
            return mo.group(1)
    raise RuntimeError('Unable to find version string in %s.' % (VERSIONFILE,))

if sys.argv[-1] == 'publish':
	os.system('python setup.py sdist upload')
	sys.exit()

setup(
	name=u('augure'),
	version=get_version(),
	description=u('## Set description'),
	long_description=open('README.md').read(),
	license=open('LICENSE').read(),
	author=u('Tristan Carranante'),
	author_email=u('tristan@carranante.name'),
	url='## Set url',
	keywords=u('## Set keywords'),
	packages=['augure'],
    scripts=['scripts/augure'],
	install_requires=['envelopes','schedule','requests'],
	classifiers=[
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
		'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3']
)
