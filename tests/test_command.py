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
    create_from_template(filename, str(tmpdir.join(filename)),
            distname='testdistname')
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


@pytest.mark.randomize(('package', str), ncalls=5)
def test_generate_recipe_with_missing_distdir(tmpdir, package):
    sys.argv = ['alnair', 'generate', 'recipe', package]
    from alnair import command
    command.generate.RECIPES_DIR = str(tmpdir)
    with pytest.raises(SystemExit):
        command.main()
    tmpdir.remove()


@pytest.mark.randomize(('package', str), ncalls=5)
def test_generate_recipe_with_single_dist(tmpdir, package):
    sys.argv = ['alnair', 'generate', 'recipe', package]
    tmpdir.mkdir('dist')
    from alnair import command
    command.generate.RECIPES_DIR = str(tmpdir)
    command.main()
    with open(str(tmpdir.join('dist', '%s.py' % package))) as f:
        actual = f.read()
    with open(os.path.join(templates_dir, 'recipe.py.template')) as f:
        expected = f.read() % dict(package=package)
    assert actual == expected
    tmpdir.remove()


@pytest.mark.randomize(('package', str), ('dists', [str, str]), fixed_length=8,
        ncalls=5)
def test_generate_recipe_with_multiple_dist(tmpdir, package, dists):
    sys.argv = ['alnair', 'generate', 'recipe', package]
    for d in dists:
        tmpdir.mkdir(d)
    from alnair import command
    command.generate.RECIPES_DIR = str(tmpdir)
    command.main()
    for d in dists:
        assert tmpdir.join(d, '%s.py' % package).check()
        with open(str(tmpdir.join(d, '%s.py' % package))) as f:
            actual = f.read()
        with open(os.path.join(templates_dir, 'recipe.py.template')) as f:
            expected = f.read() % dict(package=package)
        assert actual == expected
    tmpdir.remove()


@pytest.mark.randomize(('package', str), fixed_length=8, ncalls=5)
def test_generate_recipe_with_skip_if_file_exists(tmpdir, package):
    sys.argv = ['alnair', 'generate', 'recipe', package]
    tmpdir.mkdir('dist').join('%s.py' % package).write('testdata')
    from alnair import command
    command.generate.RECIPES_DIR = str(tmpdir)
    command.main()
    with open(str(tmpdir.join('dist', '%s.py' % package))) as f:
        actual = f.read()
    assert actual == 'testdata'
    tmpdir.remove()


@pytest.mark.parametrize(('opt',), [
    ('-f',), ('--force',),
    ])
@pytest.mark.randomize(('package', str), fixed_length=8, ncalls=5)
def test_generate_recipe_with_overwrite_if_file_exists(tmpdir, package, opt):
    sys.argv = ['alnair', 'generate', 'recipe', opt, package]
    tmpdir.mkdir('dist').join('%s.py' % package).write('testdata')
    from alnair import command
    command.generate.RECIPES_DIR = str(tmpdir)
    command.main()
    with open(str(tmpdir.join('dist', '%s.py' % package))) as f:
        actual = f.read()
    with open(os.path.join(templates_dir, 'recipe.py.template')) as f:
        expected = f.read() % dict(package=package)
    assert actual == expected
    tmpdir.remove()


@pytest.mark.randomize(('packages', [str, str]), ncalls=5)
def test_generate_recipe_with_multiple_packages(tmpdir, packages):
    sys.argv = ['alnair', 'generate', 'recipe'] + packages
    tmpdir.mkdir('dist')
    from alnair import command
    command.generate.RECIPES_DIR = str(tmpdir)
    command.main()
    for package in packages:
        with open(str(tmpdir.join('dist', '%s.py' % package))) as f:
            actual = f.read()
        with open(os.path.join(templates_dir, 'recipe.py.template')) as f:
            expected = f.read() % dict(package=package)
        assert actual == expected
    tmpdir.remove()
