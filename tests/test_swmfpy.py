#!/usr/bin/env python
"""Tests for web.py
"""
import datetime as dt
from os.path import isfile
from swmfpy import *

TIMES = (dt.datetime(2012, 12, 1), dt.datetime(2013, 1, 1))


def test_write_imf_from_omni():
    write_imf_from_omni(*TIMES)
    assert isfile('IMF.dat')

