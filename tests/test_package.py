# -*- coding: utf-8 -*-

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
        setup = alnair.package.Setup()
        assert setup.after is None
        assert setup._config == {}

    @pytest.mark.randomize(('filename', str), ncalls=5)
    def test_config(self, filename):
        setup = alnair.package.Setup()
        config = setup.config(filename)
        assert isinstance(config, alnair.package.Config)
        assert len(setup._config) == 1
        assert setup._config == {filename: config}

    @pytest.mark.parametrize(('filenames',),
        # [([1],), ([1, 2],), ([1, 2, 3],), ...]
        [(list(range(1, x)),) for x in range(2, 12)])
    def test_config_multiple(self, filenames):
        setup = alnair.package.Setup()
        configs = {}
        for name in filenames:
            configs[name] = setup.config(name)
        assert setup._config == configs

    @pytest.mark.parametrize(('filenames',),
        # [([1],), ([1, 2],), ([1, 2, 3],), ...]
        [(list(range(1, x)),) for x in range(2, 12)])
    def test_config_all(self, filenames):
        setup = alnair.package.Setup()
        configs = {}
        for name in filenames:
            configs[name] = setup.config(name)
        setup._config = configs
        assert setup.config_all == configs


class TestPackage(object):
    @pytest.mark.randomize(('name', str), ncalls=5)
    def test_init(self, name):
        package = alnair.Package(name)
        assert package.name == name
        assert isinstance(package.setup, alnair.package.Setup)
