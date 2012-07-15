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

import argparse
import os
import sys

from contextlib import nested
from glob import glob

from alnair import __version__, Distribution


def fail(msg):
    sys.stderr.write('alnair: error: %s\n' % msg)
    sys.exit(1)


def create_from_template(filename, outputpath, **kwargs):
    templatedir = os.path.join(os.path.dirname(__file__), 'templates')
    fpath = os.path.join(templatedir, '%s.template' % filename)
    print u"creating file: %s" % outputpath
    with nested(open(fpath), open(outputpath, 'w')) as (rf, wf):
        wf.write(rf.read() % kwargs)


class subcommand(object):
    def __init__(self, subparsers):
        cls = self.__class__
        parser = subparsers.add_parser(cls.__name__.lower(), help=cls.__doc__,
                description=cls.__doc__)
        self.define_args(parser, cls)
        subcmds = [(n, v) for n, v in cls.__dict__.iteritems() if hasattr(v,
            '_subcommand')]
        if subcmds:
            subparser = parser.add_subparsers(title=u"subcommands")
        for name, val in subcmds:
            parser_subcommand = subparser.add_parser(name, help=val.__doc__,
                    description=val.__doc__)
            self.define_args(parser_subcommand, val)
        if hasattr(cls, 'alias'):
            subparsers.add_parser(cls.alias, description=cls.__doc__,
                    parents=[parser], add_help=False)

    def define_args(self, parser, cls):
        for args, kwargs in getattr(cls, 'args', []):
            parser.add_argument(*args, **kwargs)
        if hasattr(cls, 'execute'):
            parser.set_defaults(command=cls.execute)

    @classmethod
    def define(cls, klass):
        klass._subcommand = True
        return klass


@subcommand.define
class generate(subcommand):
    """generate the recipes template (alias "g")"""

    alias = 'g'
    RECIPES_DIR = 'recipes'

    @subcommand.define
    class template(object):
        """generate new template set"""

        args = [
            (['distname'], dict(
                metavar='DISTNAME',
                help=u"name of the distribution (e.g. archlinux)",
                )),
            (['directory'], dict(
                metavar='DIRECTORY',
                default='.',
                nargs='?',
                help=u"directory in which the recipes file layout will be"
                     u" generated (default: %(default)s)",
                )),
            ]

        @classmethod
        def execute(cls, distname, directory):
            path = os.path.join(directory, generate.RECIPES_DIR, distname)
            print u"creating directory: %s" % path
            os.makedirs(path, mode=0o755)
            outputpath = os.path.join(path, 'common.py')
            create_from_template('common.py', outputpath=outputpath,
                    distname=distname)

    @subcommand.define
    class recipe(object):
        """generate recipe template"""

        args = [
            (['packages'], dict(
                metavar='PACKAGE',
                nargs='+',
                help=u"name of package(s)",
                )),
            (['-f', '--force'], dict(
                dest='force',
                action='store_true',
                help=u"overwrite existent files",
                )),
            ]

        @classmethod
        def execute(cls, packages, force):
            distdirs = [d for d in glob(os.path.join(generate.RECIPES_DIR, '*')) if os.path.isdir(d)]
            if not distdirs:
                fail(
                    u"recipes directory is not exists\n"
                    u"please run `alnair generate template [DISTNAME]` first.")
            for distdir in distdirs:
                for package in packages:
                    outputpath = os.path.join(distdir, '%s.py' % package)
                    if os.path.isfile(outputpath) and force is False:
                        print u'file "%s" is exists, skipped' % outputpath
                        continue
                    create_from_template('recipe.py', outputpath=outputpath,
                            package=package)


@subcommand.define
class setup(subcommand):
    """install and setup package(s) to server from recipe(s) (alias "s")"""

    alias = 's'
    args = [
        (['distname'], dict(
            metavar='DISTNAME',
            help=u"name of the distribution (e.g. archlinux)",
            )),
        (['packages'], dict(
            metavar='PACKAGE',
            nargs='+',
            help=u"name of package(s) to installation",
            )),
        (['--host'], dict(
            dest='hosts',
            metavar='HOST',
            help=u"server hostname. If you want to target more than one host,"
                 u" please hostnames separated by commas",
            )),
        ]

    @classmethod
    def execute(cls, distname, packages, hosts):
        with Distribution(distname) as dist:
            if hosts is None:
                dist.install(packages)
            else:
                from fabric.api import env
                for host in (h.strip() for h in hosts.split(',')):
                    env.host_string = host
                    dist.install(packages)


@subcommand.define
class config(subcommand):
    """configure package(s) from recipe(s) (alias "c")"""

    alias = 'c'
    args = setup.args

    @classmethod
    def execute(cls, distname, packages, hosts):
        with Distribution(distname) as dist:
            if hosts is None:
                dist.config(packages)
            else:
                from fabric.api import env
                for host in (h.strip() for h in hosts.split(',')):
                    env.host_string = host
                    dist.config(packages)


def main():
    parser = argparse.ArgumentParser(description=u"alnair command-line interface.")
    parser.add_argument('--version', action='version',
            version='%(prog)s ' + __version__)
    subparsers = parser.add_subparsers(title=u"commands")
    for cls in (c for c in globals().values() if hasattr(c, '_subcommand') and
            issubclass(c, subcommand)):
        cls(subparsers)
    args = parser.parse_args().__dict__
    command = args.pop('command')
    command(**args)
