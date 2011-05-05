# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2009-2011, Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import yaml
import taboot.runner
from optparse import OptionParser
from taboot import __version__


class MalformedYAML(Exception):
    pass


def resolve_types(ds, relative_to):
    """
    Recursively translate string representation of a type within a
    datastructure into an actual type instance.

    :Parameters:
      - `ds`: An arbitrary datastructure.  Within `ds`, if a dict key named
        `type` is encountered, the string contained there is replaced with the
        actual type named.
      - `relative_to`: The prefix which types are relative to; used during
        import.  As an example, if `relative_to`='taboot.tasks' and `ds`
        contains a `type` key `command.Run`, then the type is imported as
        `taboot.tasks.command.Run`.
    """
    __import__(relative_to)

    if isinstance(ds, list):
        result = []
        for item in ds:
            result.append(resolve_types(item, relative_to))
        return result
    elif isinstance(ds, dict):
        result = {}
        for k, v in ds.iteritems():
            if k == 'type':
                tokens = v.split('.')
                if len(tokens) == 1:
                    result[k] = getattr(sys.modules[relative_to], tokens[0])
                else:
                    pkg = "%s.%s" % (relative_to, tokens[0])
                    __import__(pkg)
                    result[k] = getattr(sys.modules[pkg], tokens[1])
            else:
                result[k] = resolve_types(v, relative_to)
        return result
    else:
        return ds


def build_runner(ds):
    """
    Build a :class:`taboot.runner.Runner` instance from the given
    datastructure.

    :Parameters:
      - `ds`: Datastructure roughly representing keyword arguments to be used
        when instantiating runner.  All types are processed through
        :function:`resolve_types` before handing off for instantiation.
    """
    ds['tasks'] = resolve_types(ds['tasks'], 'taboot.tasks')
    if 'output' in ds:
        ds['output'] = resolve_types(ds['output'], 'taboot.output')
    if 'preflight' in ds:
        ds['preflight'] = resolve_types(ds['preflight'], 'taboot.tasks')
    return taboot.runner.Runner(**ds)


def main():
    """
    Main function.
    """

    checkonly = False
    nopreflight = False
    usage = """taboot [OPTIONS...] [FILE...]

Run a Taboot release script.

Options:
  FILE            Release file in YAML format. Reads from stdin if FILE
                  is '-' or not given. Multiple FILEs can be given.
  -V, --version   Show program's version number and exit.
  -h, --help      Show this help message and exit.
  -n              Don't execute the release, just check script syntax.
  -s              Skip preflight sections if they exist.

Taboot is a tool for written for scripting and automating the task of
performing software releases in a large-scale infrastructure. Release
scripts are written using YAML syntax.


Taboot home page: <https://fedorahosted.org/Taboot/>
Copyright 2009-2011, Red Hat, Inc
Taboot is released under the terms of the GPLv3+ license"""

    args = sys.argv[1:]

    if "-h" in args or "--help" in args:
        print usage
        sys.exit()

    if "-V" in args or "--version" in args:
        print "Taboot v%s" % __version__
        sys.exit()

    if "-n" in args:
        checkonly = True
        i = args.index("-n")
        del args[i]

    if "-s" in args:
        nopreflight = True
        i = args.index("-s")
        del args[i]

    if len(args) >= 1:
        input_files = args
    else:
        input_files = ['-']

    for infile in input_files:
        if infile == '-':
            blob = sys.stdin.read()
        else:
            blob = open(infile).read()

        try:
            ds = yaml.load(blob)
        except:
            msg = "Please check the validity of your YAML in '%s'" % infile
            raise MalformedYAML(msg)

        if nopreflight:
            for b in ds:
                if 'preflight' in b:
                    del b['preflight']

        for runner_source in ds:
            runner = build_runner(runner_source)
            if not checkonly and not runner.run():
                break

if __name__ == '__main__':
    main()
