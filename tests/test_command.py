# -*- coding: utf-8 -*-

import os
import sys

import pytest

templates_dir = os.path.join(os.path.dirname(__file__), '..', 'alnair',
        'templates')


@pytest.mark.parametrize(('filename',), [
    ('common.py',),
    ])
def test_create_from_template(tmpdir, filename):
    # precondition
    assert not tmpdir.join(filename).check()

    # test
    from alnair.command import create_from_template
    create_from_template(filename, str(tmpdir), distname='testdistname')
    origpath = os.path.join(templates_dir, '%s.template' % filename)
    expected = open(origpath).read() % dict(distname='testdistname')
    assert open(str(tmpdir.join(filename))).read() == expected
    tmpdir.remove()


@pytest.mark.randomize(('distname', str), ncalls=5)
def test_generate_template(tmpdir, distname):
    sys.argv = ['alnair', 'generate', 'template', distname, str(tmpdir)]
    from alnair.command import main
    main()
    with open(os.path.join(templates_dir, 'common.py.template')) as f:
        expected = f.read() % dict(distname=distname)
    with open(str(tmpdir.join('recipes').join(distname).join('common.py'))) \
            as f:
        actual = f.read()
    assert tmpdir.join('recipes').join(distname).check()
    assert actual == expected
    tmpdir.remove()
