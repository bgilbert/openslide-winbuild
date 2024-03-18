#!/usr/bin/env python3
#
# Tools for building OpenSlide and its dependencies
#
# Copyright (c) 2023 Benjamin Gilbert
# All rights reserved.
#
# This script is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License, version 2.1,
# as published by the Free Software Foundation.
#
# This script is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this script. If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import annotations

import os
from pathlib import Path
import shutil
import sys

# handle our own PYTHONPATH prepending, since meson can't set environment
# variables for dist scripts
# flake8 isn't happy about this
sys.path.insert(0, os.environ['MESON_SOURCE_ROOT'])

from common.argparse import TypedArgs  # noqa: E402
from common.meson import meson_introspect, meson_source_root  # noqa: E402
from common.python import pyproject_to_message  # noqa: E402


class Args(TypedArgs):
    introspect: str


args = Args(
    'postprocess-sdist', description='Modify sdist directory before packing.'
)
args.add_arg(
    '-i', '--introspect', required=True, help='Meson introspect command'
)
args.parse()
os.environ['MESONINTROSPECT'] = args.introspect
src = meson_source_root()
dest = Path(os.environ['MESON_DIST_ROOT'])

# remove those parts of .github not ignored from .gitattributes
shutil.rmtree(dest / '.github')

# pin openslide-bin version suffix
version: str = meson_introspect('projectinfo')['version']
try:
    suffix = version.split('+', 1)[1]
except IndexError:
    suffix = ''
(dest / 'suffix').write_text(suffix + '\n')

# create Python source distribution metadata
pyproject = (
    (src / 'artifacts' / 'python' / 'pyproject.in.toml')
    .read_text()
    .replace('@version@', version)
)
(dest / 'pyproject.toml').write_text(pyproject)
(dest / 'PKG-INFO').write_bytes(pyproject_to_message(pyproject).as_bytes())
