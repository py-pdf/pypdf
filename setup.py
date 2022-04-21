#!/usr/bin/env python

import re

from setuptools import setup

VERSIONFILE = "PyPDF2/_version.py"
with open(VERSIONFILE, "rt") as fp:
    verstrline = fp.read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE))

setup(version=verstr)
