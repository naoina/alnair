# -*- coding: utf-8 -*-

from alnair import Package

pkg1 = Package('pkg1')
pkg1.setup.config('test_conffile1').contents("testdata1")
