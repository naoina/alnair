# -*- coding: utf-8 -*-

import pytest

import alnair

class TestCommand(object):
    def getattr(self, inst, attr):
        return object.__getattribute__(inst, attr)

    @pytest.mark.randomize(('arg', str), ncalls=5)
    def test_init(self, arg):
        cmd = alnair.Command(arg=arg)
        assert self.getattr(cmd, '_commands') == []
        assert self.getattr(cmd, '_current_cmd') is None
        assert self.getattr(cmd, '_arg') == arg

    @pytest.mark.parametrize(('attr', 'expected'), [
        ('_commands', []), ('_current_cmd', None), ('_arg', '')])
    def test_getattribute_attr_exists(self, attr, expected):
        cmd = alnair.Command()
        assert cmd.__getattribute__(attr) == expected

    @pytest.mark.randomize(('attr', str), ncalls=5)
    def test_getattribute_attr_to_current(self, attr):
        cmd = alnair.Command()
        assert cmd.__getattribute__(attr) is cmd
        assert self.getattr(cmd, '_current_cmd') == attr

    @pytest.mark.randomize(('attr', str), ncalls=5)
    def test_calls_with_single_attr(self, attr):
        cmd = alnair.Command()
        assert cmd.__getattribute__(attr)() is cmd
        assert self.getattr(cmd, '_commands') == [attr]

    @pytest.mark.randomize(('attr1', str), ('attr2', str), ncalls=5)
    def test_calls_with_multiple_attr(self, attr1, attr2):
        cmd = alnair.Command()
        assert cmd.__getattribute__(attr1)().__getattribute__(attr2)() is cmd
        assert self.getattr(cmd, '_commands') == [attr1, attr2]

    @pytest.mark.randomize(('attr', str), ('args', str), fixed_length=8,
            ncalls=5)
    def test_calls_with_args(self, attr, args):
        cmd = alnair.Command()
        assert cmd.__getattribute__(attr)(*args) is cmd
        assert self.getattr(cmd, '_commands') == ['%s %s' % (attr, ' '.join(args))]

    @pytest.mark.randomize(('attr', str), ('arg', str), fixed_length=8,
            ncalls=5)
    def test_calls_with_default_arg(self, attr, arg):
        cmd = alnair.Command(arg)
        assert cmd.__getattribute__(attr)() is cmd
        assert self.getattr(cmd, '_commands') == ['%s %s' % (attr, arg)]

    @pytest.mark.randomize(('attr', str), ('option', str), fixed_length=8,
            ncalls=5)
    def test_calls_with_option(self, attr, option):
        cmd = alnair.Command()
        assert cmd.__getattribute__(attr)(option=option) is cmd
        assert self.getattr(cmd, '_commands') == ['%s %s' % (attr, option)]

    @pytest.mark.randomize(('attr', str), ('arg', str), ('args', str),
            ('option', str), fixed_length=8, ncalls=5)
    def test_calls_with_all(self, attr, arg, args, option):
        cmd = alnair.Command(arg)
        assert cmd.__getattribute__(attr)(*args, option=option) is cmd
        assert self.getattr(cmd, '_commands') == \
                ['%s %s %s %s' % (attr, option, ' '.join(args), arg)]


class TestConfig(object):
    def getattr(self, inst, attr):
        return object.__getattribute__(inst, attr)

    @pytest.mark.randomize(('filename', str), ncalls=5)
    def test_init(self, filename):
        config = alnair.package.Config(filename=filename)
        assert self.getattr(config, '_filename') == filename
        assert self.getattr(config, '_contents') is None

    @pytest.mark.randomize(('contents', str), ncalls=5)
    def test_set_contents(self, contents):
        config = alnair.package.Config('dummy')
        assert config.contents(contents) is config
        assert self.getattr(config, '_contents') == contents

    @pytest.mark.parametrize(('attr', 'expected'), [
        ('_filename', 'dummy'), ('_contents', None), ('_current_cmd', None)])
    def test_getattribute_attr_exists(self, attr, expected):
        config = alnair.package.Config('dummy')
        assert config.__getattribute__(attr) == expected

    @pytest.mark.randomize(('attr', str), ncalls=5)
    def test_getattribute_attr_to_current(self, attr):
        config = alnair.package.Config('dummy')
        assert config.__getattribute__(attr) is config
        assert self.getattr(config, '_current_cmd') == attr


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
