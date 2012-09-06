# -*- coding: utf-8 -*-

from alnair import Package

pkghost1 = Package('pkghost1')

with pkghost1.host('testhost1'):
    pkghost1.setup.config('testhost_conffile1').contents("testhostdata1")
