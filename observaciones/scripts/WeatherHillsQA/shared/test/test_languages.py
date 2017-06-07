# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals
from nose.tools import assert_equal
from util.languages import *


def test_map_chars():
    char_map = {'ó': 'o', 'ą': 'a', 'ź': 'z', 'ż': 'z', 'ń': 'n'}

    assert_equal('zyzn', map_chars('żyźń', char_map))
    assert_equal('ćn', map_chars('ćń', char_map))



