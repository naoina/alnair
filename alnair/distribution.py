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

import imp
import os

from io import StringIO

import fabric.api as fa

from alnair.exception import (
    NoSuchDirectoryError,
    NoSuchFileError,
    UndefinedPackageError,
    )
from alnair.package import Command, Package


class Distribution(object):
    CONFIG_DIR = os.path.abspath('recipes')

    def __init__(self, name, install_command=None):
        """Constructor of Distribution class

        :param name: distribution name (e.g. 'archlinux')
        :param install_command: install command (e.g. 'pacman -S')
        """
        self.name = name
        self.install_command = install_command
        self._within_context = False
        self._packages = []

    def install(self, pkgs, *args, **kwargs):
        """Install packages to a remote server

        An arguments types are instance of :class:`alnair.package.Package` or
        string.
        If kwargs is provided, mapping to instance variable (e.g.
        self.install_command). But in fact, instance variables do not
        change.

        :param pkgs: package name string or instance of
            :class:`alnair.package.Package` or iterable of it
        :param *args: iterable of package name string or instance of
            :class:`alnair.package.Package`
        :returns: True if install successful, otherwise False
        """
        args = list(args)
        if hasattr(pkgs, '__iter__'):
            args.extend(pkgs)
        else:
            args.append(pkgs)
        self._packages = packages = self.get_packages(args)
        install_command = self.get_install_command(
                kwargs.get('install_command'))
        pkgs = ' '.join(pkg.name for pkg in packages)
        success = fa.sudo('%s %s' % (install_command, pkgs)).succeed
        if success and not self._within_context:
            self.after_install()
        return success

    def after_install(self):
        for pkg in self._packages:
            setup = pkg.setup
            for filename, config in setup.config_all:
                sio = StringIO(config._contents.decode('utf-8'))
                fa.put(sio, filename, use_sudo=True)
                for cmd in config._cmd._commands:
                    fa.sudo(cmd)
        for cmd in self.get_after_commands(setup.after):
            fa.sudo(cmd)

    def get_after_commands(self, after):
        """Get an command of after an install

        :param after: instance of :class:`alnair.command.Command` or callable
        :returns: iterable of instance of :class:`alnair.command.Command`
        """
        if isinstance(after, Command):
            return after._commands
        elif callable(after):
            return self.get_after_commands(after())
        else:
            fa.abort(u"`after` type must be instance of"
                     u" `alnair.command.Command` or callable")

    def get_install_command(self, default_install_command=None):
        """Get an install command

        :param default_install_command: default install command
        :returns: string of install command
        """
        install_command = default_install_command or self.install_command
        if not install_command:
            common_module = imp.load_source('common',
                    os.path.join(self.CONFIG_DIR, self.name, 'common.py'))
            try:
                install_command = getattr(common_module, 'install_command')
            except AttributeError:
                fa.abort(u"`install_command` is not provided")
        return install_command

    def get_packages(self, packages):
        """Get a packages

        All package name string in packages, normalize to an instance of
        :class:`alnair.package.Package` .
        An instance of :class:`alnair.package.Package` in packages, including
        the result as it is.

        :param packages: iterable object of instance of
            :class:`alnair.package.Package` or string of package name
        :returns: list of instance of :class:`alnair.package.Package`
        """
        result = []
        for pkg in packages:
            if isinstance(pkg, basestring):
                try:
                    result.append(self.get_package(pkg))
                except (NoSuchDirectoryError, NoSuchFileError,
                        UndefinedPackageError, TypeError) as exc:
                    fa.abort(exc.message)
            elif isinstance(pkg, Package):
                result.append(pkg)
            else:
                fa.abort(u"provided package types must be Package instance or"
                         u" string")
        return result

    def get_package(self, pkg):
        """Get a package from file

        :param pkg: string of package name
        :returns: instance of :class:`alnair.package.Package`
        """
        if not os.path.isdir(self.CONFIG_DIR):
            raise NoSuchDirectoryError(u"no such configuration directory `%s`"
                    % self.CONFIG_DIR)
        configfile = os.path.join(self.CONFIG_DIR, self.name,
                '%s.py' % pkg)
        print configfile
        if not os.path.isfile(configfile):
            raise NoSuchFileError(u"no such configuration file `%s`" %
                    configfile)
        module = imp.load_source(pkg, configfile)
        try:
            pkginst = getattr(module, pkg)
        except AttributeError:
            raise UndefinedPackageError(u"`%s` variable must be defined and"
                    u" instance of Package" % pkg)
        if not isinstance(pkginst, Package):
            raise TypeError(u"`%s` variable must be instance of Package,"
                    u"but %s" % (pkg, type(pkg)))
        return pkginst

    def __enter__(self):
        self._within_context = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._within_context = False
        if not exc_type:
            self.after_install()
        return False
