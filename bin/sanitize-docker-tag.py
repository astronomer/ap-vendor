#!/usr/bin/env python3
"""Replace characters that are unsafe in a docker tag with an underscore."""

import sys
from functools import reduce

# Explicit set of characters that are forbidden in a docker tag
forbidden = """ !"#$%&'()*+,/:;<=>?@[\\]^`{|}~"""
tag = reduce(lambda acc, x: acc.replace(x, "_"), forbidden, sys.argv[1])

# First char must be in the given list of characters.
if tag[0] not in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz":
    tag = "_" + tag[1:]

tag = tag[:128]

print(tag)
