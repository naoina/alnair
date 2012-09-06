# -*- coding: utf-8 -*-

import os

import pytest

import alnair


class TestCommand(object):
    @pytest.mark.randomize(('arg', str), ncalls=5)
    def test_init(self, arg):
        cmd = alnair.Command(arg=arg)
        assert cmd._commands == []
        assert cmd._arg == arg

    @pytest.mark.randomize(('cmd', str), ncalls=5)
    def test_runs(self, cmd):
        import fabric.api as fa
        cmd = alnair.Command()
        cmd.run(cmd)
        assert cmd._commands == [(cmd, fa.run)]

        cmd.run(cmd)
        assert cmd._commands == [(cmd, fa.run), (cmd, fa.run)]

    @pytest.mark.randomize(('cmd', str), ncalls=5)
    def test_sudos(self, cmd):
        import fabric.api as fa
        cmd = alnair.Command()
        cmd.sudo(cmd)
        assert cmd._commands == [(cmd, fa.sudo)]

        cmd.sudo(cmd)
        assert cmd._commands == [(cmd, fa.sudo), (cmd, fa.sudo)]


class TestConfig(object):
    @pytest.mark.randomize(('filename', str), ncalls=5)
    def test_init(self, filename):
        config = alnair.package.Config(filename=filename)
        assert config._filename == filename
        assert config._contents is None

    @pytest.mark.randomize(('contents', str), ncalls=5)
    def test_set_contents(self, contents):
        config = alnair.package.Config('dummy')
        assert config.contents(contents) is config
        assert config._contents == contents


class TestSetup(object):
    def test_init(self):
        setup = alnair.package.Setup(alnair.package.Host())
        assert isinstance(setup._host, alnair.package.Host)
        assert setup.after is None
        assert setup._config == {}

    @pytest.mark.randomize(('hostname', str), ('filename', str), ncalls=5)
    def test_config(self, hostname, filename):
        host = alnair.package.Host()
        host.name = hostname
        setup = alnair.package.Setup(host)
        config = setup.config(filename)
        assert isinstance(config, alnair.package.Config)
        assert len(setup._config) == 1
        assert setup._config == {(hostname, filename): config}

    @pytest.mark.parametrize(('filenames',),
        # [([1],), ([1, 2],), ([1, 2, 3],), ...]
        [(list(range(1, x)),) for x in range(2, 12)])
    @pytest.mark.randomize(('hostname', str), ncalls=5)
    def test_config_multiple(self, hostname, filenames):
        host = alnair.package.Host()
        host.name = hostname
        setup = alnair.package.Setup(host)
        configs = {}
        for name in filenames:
            configs[(hostname, name)] = setup.config(name)
        assert setup._config == configs

    @pytest.mark.parametrize(('filenames',),
        # [([1],), ([1, 2],), ([1, 2, 3],), ...]
        [(list(range(1, x)),) for x in range(2, 12)])
    @pytest.mark.randomize(('hostname', str), ncalls=5)
    def test_config_all(self, hostname, filenames):
        host = alnair.package.Host()
        host.name = hostname
        setup = alnair.package.Setup(host)
        configs = {}
        for name in filenames:
            configs[(hostname, name)] = setup.config(name)
        setup._config = configs
        assert setup.config_all == configs


class TestPackage(object):
    @pytest.mark.randomize(('name', str), ncalls=5)
    def test_init_with_name(self, name):
        package = alnair.Package(name)
        assert package.name == (name,)
        assert isinstance(package._host, alnair.package.Host)
        assert isinstance(package.setup, alnair.package.Setup)

    @pytest.mark.randomize(('names', [str, str, str]), ncalls=5)
    def test_init_with_multiple_name(self, names):
        package = alnair.Package(names[0], *names[1:])
        assert package.name == tuple(names)
        assert isinstance(package._host, alnair.package.Host)
        assert isinstance(package.setup, alnair.package.Setup)

    def test_init_with_default(self):
        package = alnair.Package()
        expected = os.path.splitext(os.path.basename(__file__))[0]
        assert package.name == (expected,)
        assert isinstance(package._host, alnair.package.Host)
        assert isinstance(package.setup, alnair.package.Setup)

    @pytest.mark.randomize(('hostname', str), ncalls=5)
    def test_host(self, hostname):
        package = alnair.Package()
        host = package.host(hostname)
        assert isinstance(host, alnair.package.Host)
        assert host is package._host
        assert package._host.current_hostname == hostname


class TestHost(object):
    @pytest.mark.randomize(('name', str), ncalls=5)
    def test_init(self, name):
        host = alnair.package.Host()
        assert host.name is None
        assert host.current_hostname is None

    @pytest.mark.randomize(('name', str), ncalls=5)
    def test_enter(self, name):
        host = alnair.package.Host()
        assert host.name is None
        host.current_hostname = name
        with host:
            assert host.name == name

    @pytest.mark.randomize(('name', str), ncalls=5)
    def test_exit(self, name):
        host = alnair.package.Host()
        assert host.name is None
        host.current_hostname = name
        with host:
            assert host.name == name
        assert host.name is None
