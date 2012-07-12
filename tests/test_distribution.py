# -*- coding: utf-8 -*-

import contextlib
import itertools
import os

import mock
import pytest

import alnair

from io import StringIO

class TestDistribution(object):
    TEST_FIXTURE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
        'fixtures'))
    TEST_DISTRIBUTION = 'testdist'

    def setup_method(self, method):
        reload(alnair)  # reset `alnair.setup` global variable

    @pytest.mark.randomize(('name', str), ncalls=5)
    def test_init(self, name):
        dist = alnair.Distribution(name)
        assert dist.name == name
        assert dist.install_command is None
        assert dist._within_context is False
        assert dist._packages == []

    @pytest.mark.randomize(('install_command', str), ncalls=5)
    def test_init_with_install_command(self, install_command):
        dist = alnair.Distribution('dummy', install_command)
        assert dist.name == 'dummy'
        assert dist.install_command == install_command
        assert dist._within_context is False
        assert dist._packages == []

    def test_default_config_dir(self):
        expected = os.path.abspath('recipes')
        assert alnair.Distribution.CONFIG_DIR == expected

    @pytest.mark.parametrize(('pkgs',),
        [(L,) for L in itertools.combinations(['pkg1', 'pkg2', 'pkg3']
            + [alnair.Package(x) for x in ['pkg1', 'pkg2', 'pkg3']], 3)])
    def test_install(self, pkgs):
        pkg, args = pkgs[0], pkgs[1:]
        mock_pkgs = [alnair.Package(p) for p in ['pkg1', 'pkg2', 'pkg3']]
        with contextlib.nested(
                mock.patch('fabric.api.sudo'),
                mock.patch.multiple('alnair.Distribution',
                    get_packages=mock.DEFAULT,
                    get_install_command=mock.DEFAULT,
                    after_install=mock.DEFAULT)
                ) as (mock_fa_sudo, mock_dist):
            mock_dist['get_packages'].return_value = mock_pkgs
            mock_dist['get_install_command'].return_value = \
                'test_install_command'
            dist = alnair.Distribution('dummy')
            dist.install(pkg, *args)
        expected = [mock.call('test_install_command pkg1 pkg2 pkg3')]
        assert mock_fa_sudo.call_count == 1
        assert mock_fa_sudo.call_args_list == expected
        assert mock_dist['after_install'].call_count == 1

    @pytest.mark.randomize(('install_num', int), min_num=1, max_num=20,
            ncalls=1)
    def test_install_with_multiple_call_within_context(self, install_num):
        with contextlib.nested(
                mock.patch('fabric.api.sudo'),
                mock.patch.multiple('alnair.Distribution',
                    get_packages=mock.DEFAULT,
                    get_install_command=mock.DEFAULT,
                    after_install=mock.DEFAULT)
                ) as (mock_fa_sudo, mock_dist):
            mock_dist['get_install_command'].return_value = \
                'test_install_command'
            with alnair.Distribution('dummy') as dist:
                for i in range(install_num):
                    mock_dist['get_packages'].return_value = \
                        [alnair.Package('pkg%d' % i)]
                    dist.install('pkg%d' % i)
            assert mock_dist['after_install'].call_count == 1
            assert [p.name for p in dist._packages] == \
                    ['pkg%d' % x for x in range(install_num)]

    @pytest.mark.parametrize(('pkgnames', 'confnames', 'testdata'),
        # [([],), (['pkg1'], ['test_conffile1'], ['testdata1']),
        #   (['pkg1', 'pkg2'], ['test_conffile1', 'test_conffile2'],
        #       ['testdata1', 'testdata2']),
        #   (['pkg1', 'pkg2', 'pkg3'],
        #       ['test_conffile1', 'test_conffile2', 'test_conffile3'],
        #       ['testdata1', 'testdata2', 'testdata3'])]
        [(['pkg%d' % x for x in range(1, y)],
            ['test_conffile%d' % x for x in range(1, y)],
            ['testdata%d' % x for x in range(1, y)]) for y in range(1, 5)])
    def test_config_with_str(self, pkgnames, confnames, testdata):
        with mock.patch('fabric.api.put') as mock_put:
            dist = alnair.Distribution(self.TEST_DISTRIBUTION)
            dist.CONFIG_DIR = self.TEST_FIXTURE_DIR
            dist.config(pkgnames)
            assert mock_put.call_count == len(pkgnames)
            for arg, c, d in zip(mock_put.call_args_list, confnames, testdata):
                sio = arg[0][0]
                assert isinstance(sio, StringIO)
                assert arg[0][1] == c
                assert sio.read() == d

    @pytest.mark.parametrize(('pkgs', 'confnames', 'testdata'),
        # [([],), ([pkg1], ['test_conffile1'], ['testdata1']),
        #   ([pkg1, pkg2], ['test_conffile1', 'test_conffile2'],
        #       ['testdata1', 'testdata2']),
        #   ([pkg1, pkg2, pkg3],
        #       ['test_conffile1', 'test_conffile2', 'test_conffile3'],
        #       ['testdata1', 'testdata2', 'testdata3'])]
        [([alnair.Package('pkg%d' % x) for x in range(1, y)],
            ['test_conffile%d' % x for x in range(1, y)],
            ['testdata%d' % x for x in range(1, y)]) for y in range(1, 5)])
    def test_config_with_package(self, pkgs, confnames, testdata):
        for p, c, t in zip(pkgs, confnames, testdata):
            p.setup.config(c).contents(t)
        with mock.patch('fabric.api.put') as mock_put:
            dist = alnair.Distribution('dummy')
            dist.config(pkgs)
            assert mock_put.call_count == len(pkgs)
            for arg, c, d in zip(mock_put.call_args_list, confnames, testdata):
                sio = arg[0][0]
                assert isinstance(sio, StringIO)
                assert arg[0][1] == c
                assert sio.read() == d

    @pytest.mark.parametrize(('pkgs', 'confnames', 'testdata'),
        [(['pkg%d' % x for x in range(1, y)] +
                [alnair.Package('pkg%d' % x) for x in range(1, y)],
            ['test_conffile%d' % x for x in range(1, y)],
            ['testdata%d' % x for x in range(1, y)]) for y in range(1, 5)])
    def test_config_with_mixed(self, pkgs, confnames, testdata):
        for p, c, t in zip([x for x in pkgs if isinstance(x, alnair.Package)],
                confnames, testdata):
            if isinstance(p, alnair.Package):
                p.setup.config(c).contents(t)
        with mock.patch('fabric.api.put') as mock_put:
            dist = alnair.Distribution(self.TEST_DISTRIBUTION)
            dist.CONFIG_DIR = self.TEST_FIXTURE_DIR
            dist.config(pkgs)
            assert mock_put.call_count == len(pkgs)
            for arg, c, d in zip(mock_put.call_args_list, confnames, testdata):
                sio = arg[0][0]
                assert isinstance(sio, StringIO)
                assert arg[0][1] == c
                assert sio.read() == d

    def test_config_with_global_setup_config(self):
        with mock.patch('fabric.api.put') as mock_put:
            dist = alnair.Distribution('dummy')
            alnair.setup.config('testconfig').contents("testdata")
            dist.config([])
            assert mock_put.call_count == 1
            sio = mock_put.call_args[0][0]
            assert isinstance(sio, StringIO)
            assert mock_put.call_args[0][1] == 'testconfig'
            assert sio.read() == "testdata"

    @pytest.mark.parametrize(('after',), [
        (mock.Mock(spec=alnair.Command),), (None,)])
    @pytest.mark.randomize(('num', int), min_num=1, max_num=20, ncalls=1)
    def test_after_install(self, after, num):
        packages = []
        setup_calls = []
        conf_calls = []
        after_calls = []
        for i in range(num):
            pkg = mock.Mock(spec=alnair.Package)
            setup = mock.Mock(spec=alnair.package.Setup)
            config = mock.Mock(spec=alnair.package.Config)
            func = mock.Mock()
            config._contents = 'testcontents%d' % i
            config._commands = [('confcmd%d' % i, func)]
            setup._commands = [('setupcmd%d' % i, func)]
            pkg.setup = setup
            pkg.setup.config_all = {'name%d' % i: config}
            pkg.setup.after = after
            packages.append(pkg)
            setup_calls.append(mock.call(setup))
            conf_calls.append(mock.call(config))
            after_calls.append(mock.call(after))
        with contextlib.nested(
                mock.patch.multiple('fabric.api', sudo=mock.DEFAULT,
                    put=mock.DEFAULT),
                mock.patch('alnair.Distribution.get_after_command',
                    return_value=after),
                mock.patch('alnair.Distribution.exec_commands'),
                ) as (mock_fa, mock_get_after_command, mock_exec_commands):
            dist = alnair.Distribution('dummy')
            dist._packages = packages
            dist.after_install()
            call_count = 0 if after is None else num
            assert mock_get_after_command.call_count == call_count
        if after:
            expected = [x for y in zip(setup_calls, conf_calls, after_calls)
                    for x in y]  # call by get_after_command
        else:
            expected = [x for y in zip(setup_calls, conf_calls) for x in y]
        assert mock_exec_commands.call_count == (num + num + call_count)
        assert mock_exec_commands.call_args_list == expected
        assert mock_fa['put'].call_count == num

    def test_after_install_with_global_setup(self):
        with mock.patch('fabric.api.put') as mock_put:
            dist = alnair.Distribution('dummy')
            dist._packages = []
            alnair.setup.config('testconfig').contents("testdata")
            cmd = alnair.Command()
            mock_func = mock.Mock()
            cmd._commands = [('testcmd', mock_func)]
            alnair.setup.after = cmd
            dist.after_install()
            mock_put.call_count == 1
            sio = mock_put.call_args[0][0]
            assert isinstance(sio, StringIO)
            assert mock_put.call_args[0][1] == 'testconfig'
            assert sio.read() == "testdata"
            assert mock_func.call_count == 1
            assert mock_func.call_args_list == [mock.call('testcmd')]

    @pytest.mark.randomize(('num', int), min_num=1, max_num=10)
    def test_exec_commands(self, num):
        dist = alnair.Distribution('dummy')
        func = mock.Mock()
        cmd = mock.Mock(spec=alnair.Command)
        cmd._commands = [('cmd%d' % i, func) for i in range(num)]
        dist.exec_commands(cmd)
        expected = [mock.call('cmd%d' % i) for i in range(num)]
        assert func.call_args_list == expected

    def test_get_after_command_with_command(self):
        dist = alnair.Distribution('dummy')
        cmd = alnair.Command()
        assert dist.get_after_command(cmd) is cmd

    def test_get_after_command_with_callable(self):
        dist = alnair.Distribution('dummy')
        cmd = alnair.Command()
        func = mock.Mock()
        func.return_value = cmd
        assert dist.get_after_command(func) is cmd
        assert func.call_count == 1

    @pytest.mark.parametrize(('after',), [
        (1,), ('',), ([3],), ({4: '4'},)])
    def test_get_after_command_with_wrong_type(self, after):
        dist = alnair.Distribution('dummy')
        with pytest.raises(SystemExit) as exc_info:
            dist.get_after_command(after)
        assert getattr(exc_info.value, 'code', exc_info.value) == 1

    def test_get_install_command(self):
        dist = alnair.Distribution(self.TEST_DISTRIBUTION)
        dist.CONFIG_DIR = self.TEST_FIXTURE_DIR
        assert dist.get_install_command() == 'test_cmd'

    def test_get_install_command_with_exception(self):
        dist = alnair.Distribution(self.TEST_DISTRIBUTION)
        dist.CONFIG_DIR = self.TEST_FIXTURE_DIR
        with mock.patch('imp.load_source') as mock_load_source:
            mock_load_source.return_value = None
            with pytest.raises(SystemExit) as exc_info:
                dist.get_install_command()
            assert getattr(exc_info.value, 'code', exc_info.value) == 1

    @pytest.mark.randomize(('cmd', str), fixed_length=8, ncalls=5)
    def test_get_install_command_with_default(self, cmd):
        dist = alnair.Distribution('dummy', cmd)
        assert dist.get_install_command(cmd) == cmd

    @pytest.mark.randomize(('cmd', str), fixed_length=8, ncalls=5)
    def test_get_install_command_with_default_arg(self, cmd):
        dist = alnair.Distribution('dummy')
        assert dist.get_install_command(cmd) == cmd

    @pytest.mark.parametrize(('pkgnames',),
        # [([],), (['pkg1'],), (['pkg1', 'pkg2'],),
        #     (['pkg1', 'pkg2', 'pkg3'],)]
        [(['pkg%d' % x for x in range(1, y)],) for y in range(1, 5)])
    def test_get_packages_with_str(self, pkgnames):
        with mock.patch('alnair.Distribution.get_package') as mock_get_package:
            mock_get_package.side_effect = lambda pkg: alnair.Package(pkg)
            dist = alnair.Distribution('dummy')
            result = dist.get_packages(pkgnames)
            assert len(result) == len(pkgnames)
            assert all([isinstance(x, alnair.Package) for x in result])
            assert all([x.name == y for x, y in zip(result, pkgnames)])

    @pytest.mark.parametrize(('pkgs',),
        # list of alnair.Package objects
        # [([],), ([pkg1],), ([pkg1, pkg2],), ([pkg1, pkg2, pkg3],)]
        [([alnair.Package('pkg%d' % x) for x in range(1, y)],) for y in
            range(1, 5)])
    def test_get_packages_with_package(self, pkgs):
        with mock.patch('alnair.Distribution.get_package', return_value=None):
            dist = alnair.Distribution('dummy')
            result = dist.get_packages(pkgs)
            assert len(result) == len(pkgs)
            assert all([isinstance(x, alnair.Package) for x in result])
            assert all([x.name == y.name for x, y in zip(result, pkgs)])

    @pytest.mark.parametrize(('pkgs',),
        [(L,) for L in itertools.combinations(['pkg1', 'pkg2', 'pkg3'] +
            [alnair.Package(x) for x in ['pkg1', 'pkg2', 'pkg3']], 3)])
    def test_get_packages_with_mixed(self, pkgs):
        with mock.patch('alnair.Distribution.get_package') as mock_get_package:
            mock_get_package.side_effect = lambda pkg: alnair.Package(pkg)
            dist = alnair.Distribution('dummy')
            result = dist.get_packages(pkgs)
            assert len(result) == len(pkgs)
            assert all([isinstance(x, alnair.Package) for x in result])
            assert all([x.name == (getattr(y, 'name', y)) for x, y in
                zip(result, pkgs)])

    @pytest.mark.parametrize(('pkgs',),
        [(L,) for L in itertools.combinations(['pkg1', 'pkg2', 'pkg3'] +
            [alnair.Package(x) for x in ['pkg1', 'pkg2', 'pkg3']], 3)])
    def test_get_packages_with_additional_args(self, pkgs):
        with mock.patch('alnair.Distribution.get_package') as mock_get_package:
            mock_get_package.side_effect = alnair.Package
            dist = alnair.Distribution('dummy')
            pkg, additionals = pkgs[0], pkgs[1:]
            result = dist.get_packages(pkg, *additionals)
            assert len(result) == len(pkgs)
            assert sorted(x.name for x in result) == \
                    sorted(x if isinstance(x, str) else x.name for x in pkgs)

    @pytest.mark.parametrize(('exc',), [
        (alnair.NoSuchDirectoryError,), (alnair.NoSuchFileError,),
        (alnair.UndefinedPackageError,), (TypeError,),
        ])
    def test_get_packages_with_missing(self, exc):
        with mock.patch('alnair.Distribution.get_package') as mock_get_package:
            def get_package(pkg):
                raise exc
            mock_get_package.side_effect = get_package
            dist = alnair.Distribution('dummy')
            with pytest.raises(SystemExit) as exc_info:
                dist.get_packages(['dummy'])
            assert getattr(exc_info.value, 'code', exc_info.value) == 1

    @pytest.mark.parametrize(('pkg',), [
        (0,), (1,), (None,), (['pkg'],), ({'pkg': 'pkg'},)])
    def test_get_packages_with_wrong_type(self, pkg):
        dist = alnair.Distribution('dummy')
        with mock.patch('alnair.Distribution.get_package', return_value=None):
            with pytest.raises(SystemExit) as exc_info:
                dist.get_packages([pkg])
            assert getattr(exc_info.value, 'code', exc_info.value) == 1

    def test_get_package(self):
        dist = alnair.Distribution(self.TEST_DISTRIBUTION)
        dist.CONFIG_DIR = self.TEST_FIXTURE_DIR
        assert isinstance(dist.get_package('testpkg'), alnair.Package)

    def test_get_package_with_nosuch_dir(self):
        dist = alnair.Distribution(self.TEST_DISTRIBUTION)
        dist.CONFIG_DIR = '/path/to/nosuch/dir'
        with pytest.raises(alnair.NoSuchDirectoryError):
            dist.get_package('testpkg')

    def test_get_package_with_nosuch_conffile(self):
        dist = alnair.Distribution(self.TEST_DISTRIBUTION)
        dist.CONFIG_DIR = self.TEST_FIXTURE_DIR
        with pytest.raises(alnair.NoSuchFileError):
            dist.get_package('unknownpkg')

    def test_get_package_with_undefined_package(self):
        dist = alnair.Distribution(self.TEST_DISTRIBUTION)
        dist.CONFIG_DIR = self.TEST_FIXTURE_DIR
        with pytest.raises(alnair.UndefinedPackageError):
            dist.get_package('undefinedpkg')

    def test_get_package_with_wrong_package_type(self):
        dist = alnair.Distribution(self.TEST_DISTRIBUTION)
        dist.CONFIG_DIR = self.TEST_FIXTURE_DIR
        with pytest.raises(TypeError):
            dist.get_package('wrongtypepkg')

    def test_contextmanager_with_init(self):
        with mock.patch('alnair.Distribution.after_install') as \
                mock_after_install:
            mock_after_install.return_value = None
            with alnair.Distribution('dummy') as dist:
                assert isinstance(dist, alnair.Distribution)
                assert dist._within_context is True
            assert dist._within_context is False
            assert mock_after_install.call_count == 1

    def test_contextmanager_with_exception(self):
        with mock.patch('alnair.Distribution.after_install') as \
                mock_after_install:
            mock_after_install.return_value = None
            with pytest.raises(UserWarning):
                with alnair.Distribution('dummy'):
                    raise UserWarning
            assert not mock_after_install.called
