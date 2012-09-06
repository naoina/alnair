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

import inspect
import os

import fabric.api as fa


class Command(object):
    def __init__(self, arg=''):
        """Constructor of Command class

        :param arg: last argument of command
        """
        self._commands = []
        self._arg = arg

    def run(self, cmd):
        """Set a run command on the user privileges

        :param cmd: string of command
        :returns: self
        """
        self._commands.append(self._make_command(cmd, fa.run))
        return self

    def sudo(self, cmd):
        """Set a run command on the super user privileges

        :param cmd: string of command
        :returns: self
        """
        self._commands.append(self._make_command(cmd, fa.sudo))
        return self

    def _make_command(self, cmd, func):
        return (cmd, func)


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
    def __init__(self, host):
        """Constructor of Setup class

        :param host: instance of :class:`Host`
        """
        super(Setup, self).__init__()
        self._host = host
        self.after = None
        self._config = {}

    def config(self, filename):
        """Get an instance of :class:`Config`

        :param filename: filename of config file (e.g. '/etc/nginx/nginx.conf')
        :returns: instance of :class:`Config`
        """
        key = (self._host.name, filename)
        try:
            config = self._config[key]
        except KeyError:
            self._config[key] = config = Config(filename)
        return config

    @property
    def config_all(self):
        """Get an all instance of :class:`Config`

        :returns: dict of filename key and instalce of :class:`Config` value
        """
        return self._config


class Host(object):
    def __init__(self):
        """Constructor of Host class
        """
        self.name = None
        self.current_hostname = None

    def __enter__(self):
        self.name = self.current_hostname

    def __exit__(self, exc_type, exc_value, traceback):
        self.name = None


class Package(object):
    def __init__(self, name=None, *args):
        """Constructor of Package class

        :param name: name of package (e.g. 'nginx'). If not given or None,
            name is takes from filename (e.g. If filename is 'foo.py', name is
            'foo').
        :param args: name of related packages
            (e.g. 'mysql' and 'mysql-clients')
        """
        if name is None:
            filename = inspect.currentframe().f_back.f_code.co_filename
            name = os.path.splitext(os.path.basename(filename))[0]
        self.name = (name,) + args
        self._host = Host()
        self.setup = Setup(self._host)

    def host(self, hostname):
        """Set the one time hostname for context manager

        :param hostname: string of target host or IP address
        :returns: instance of :class:`Host`
        """
        self._host.current_hostname = hostname
        return self._host
