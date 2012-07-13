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

from alnair import __version__


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
    def __init__(self, subparsers, alias=None):
        cls = self.__class__
        parser = subparsers.add_parser(cls.__name__.lower(), help=cls.__doc__)
        subparser = parser.add_subparsers(title=u"subcommands")
        for name, val in cls.__dict__.iteritems():
            if hasattr(val, '_subcommand'):
                parser_subcommand = subparser.add_parser(name,
                        help=val.__doc__)
                for argdict in val.args:
                    parser_subcommand.add_argument(**argdict)
                parser_subcommand.set_defaults(command=val().execute)
        if hasattr(cls, 'alias'):
            subparsers.add_parser(cls.alias, parents=[parser], add_help=False)

    @classmethod
    def define(cls, klass):
        klass._subcommand = True
        return klass


class generate(subcommand):
    """generate the recipes template (alias "g")"""

    alias = 'g'
    RECIPES_DIR = 'recipes'

    @subcommand.define
    class template(object):
        """generate new template set"""

        args = [
            dict(
                dest='distname',
                metavar='DISTNAME',
                help=u"name of the distribution (e.g. archlinux)",
                ),
            dict(
                dest='directory',
                metavar='DIRECTORY',
                default='.',
                nargs='?',
                help=u"directory in which the recipes file layout will be"
                     u" generated (default: %(default)s)",
                ),
            ]

        def execute(self, distname, directory):
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
            dict(
                dest='package',
                metavar='PACKAGE',
                help=u"name of a package",
                ),
            ]

        def execute(self, package):
            distdirs = [d for d in glob(os.path.join(generate.RECIPES_DIR, '*')) if os.path.isdir(d)]
            if not distdirs:
                fail(
                    u"recipes directory is not exists\n"
                    u"please run `alnair generate template [DISTNAME]` first.")
            for distdir in distdirs:
                outputpath = os.path.join(distdir, '%s.py' % package)
                create_from_template('recipe.py', outputpath=outputpath,
                        package=package)


def main():
    parser = argparse.ArgumentParser(description=u"aaa")
    parser.add_argument('--version', action='version',
            version='%(prog)s ' + __version__)
    subparsers = parser.add_subparsers(title=u"commands")
    generate(subparsers)
    args = parser.parse_args().__dict__
    command = args.pop('command')
    command(**args)
