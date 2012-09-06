# -*- coding: utf-8 -*-

from alnair import Package

pkghost2 = Package('pkghost2')

with pkghost2.host('testhost1'):
    pkghost2.setup.config('testhost_conffile1').contents("testhostdata1")

with pkghost2.host('testhost2'):
    pkghost2.setup.config('testhost_conffile2').contents("testhostdata2")
