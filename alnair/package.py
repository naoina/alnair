# -*- coding: utf-8 -*-

# Copyright (c) 2012 Naoya Inada <naoina@kuune.org>
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.


__author__ = "Naoya Inada <naoina@kuune.org>"

__all__ = [
]


class Command(object):
    def __init__(self, arg=''):
        """Constructor of Command class

        :param arg: last argument of command
        """
        self._commands = []
        self._current_cmd = None
        self._arg = arg

    def __call__(self, *args, **kwargs):
        option = kwargs.get('option', '')
        command = ' '.join(s for s in (self._current_cmd, option,
            ' '.join(args), self._arg) if s).strip()
        self._commands.append(command)
        return self

    def __getattribute__(self, cmd):
        try:
            return object.__getattribute__(self, cmd)
        except AttributeError:
            object.__setattr__(self, '_current_cmd', cmd)
            return self


class Config(Command):
    def __init__(self, filename):
        """Constructor of Config class

        :param filename: filename of config file (e.g. '/etc/nginx/nginx.conf')
        """
        super(Config, self).__init__(filename)
        self._filename = filename
        self._contents = None

    def contents(self, contents):
        """Set the contents of this config

        :param contents: string of contents
        :returns: self
        """
        self._contents = contents
        return self


class Setup(Command):
    def __init__(self):
        """Constructor of Setup class
        """
        super(Setup, self).__init__()
        self.after = None
        self._config = {}

    def config(self, filename):
        """Get an instance of :class:`Config`

        :param filename: filename of config file (e.g. '/etc/nginx/nginx.conf')
        :returns: instance of :class:`Config`
        """
        try:
            config = self._config[filename]
        except KeyError:
            self._config[filename] = config = Config(filename)
        return config

    @property
    def config_all(self):
        """Get an all instance of :class:`Config`

        :returns: dict of filename key and instalce of :class:`Config` value
        """
        return self._config


class Package(object):
    def __init__(self, name):
        """Constructor of Package class

        :param name: name of package (e.g. 'nginx')
        """
        self.name = name
        self.setup = Setup()
