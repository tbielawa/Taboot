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
import argparse
import re
import datetime
import tempfile
import os
from subprocess import call
from taboot import __version__


class MalformedYAML(Exception):
    pass


def log_update(msg):
    sys.stderr.write(str(msg) + "\n")
    sys.stderr.flush()


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

    dt = datetime.datetime.today()
    defaultlogfile = "taboot-%s.log" % (dt.strftime("%Y-%m-%d-%H%M%S"))
    addLogging = False
    overrideConcurrency = False

    parser = argparse.ArgumentParser(
                 formatter_class=argparse.RawDescriptionHelpFormatter,
                 description="Run a Taboot release script.",
                 epilog="""Taboot is a tool for written for scripting \
and automating the task of
performing software releases in a large-scale infrastructure. Release
scripts are written using YAML syntax.



Taboot home page: <https://fedorahosted.org/Taboot/>
Copyright 2009-2011, Red Hat, Inc
Taboot is released under the terms of the GPLv3+ license""")

    parser.add_argument('-V', '--version', action='version',
                        version='Taboot v%s' % __version__)
    parser.add_argument('-n', '--checkonly', action='store_true',
                        default=False,
                        help='Don\'t execute the release, just check \
                              script syntax.')
    parser.add_argument('-p', '--printonly', action='store_true',
                        default=False,
                        help='Don\'t execute the release, just check \
                              script syntax and print yaml to stdout.')
    parser.add_argument('-s', '--skippreflight', action='store_true',
                        default=False,
                        help='Skip preflight sections if they exist.')
    parser.add_argument('-L', '--logfile', const=defaultlogfile, nargs='?',
                        help='Adds [LogOutput: {logfile: LOGFILE}] to the \
                              script(s) being run.  If LOGFILE is not \
                              specified then taboot-YYYY-MM-DD-HHMMSS.log \
                              will be used')
    parser.add_argument('-C', '--concurrency', nargs=1, type=int,
                        help='Sets the concurrency for the input script(s)')
    parser.add_argument('-E', '--edit', action='store_true',
                        default=False,
                        help='Edit the input script(s) before running them \
                              using $EDITOR.  If $EDITOR is undefined then \
                              emacs will be used, if emacs is not found then \
                              vi will be used.')
    parser.add_argument('input_files', nargs='*', metavar='FILE',
                        help='Release file in YAML format.  Reads from stdin \
                              if FILE is \'-\' or not given.')
    args = parser.parse_args()

    if args.logfile:
        # Since we are snarfing the next positional argument after -L, we may
        # accidentally snarf up an input yaml file.  Hence the test to see if
        # our value is a .yaml file, and if it is, we will set the logfile to
        # the default and store the yaml file name to add to input_files
        pattern = re.compile(".*yaml$", re.IGNORECASE)
        if pattern.search(args.logfile):
            # We accidentally snarfed up a yaml script, add it back to
            # input_files and use the default format
            if args.input_files:
                args.input_files.insert(0, args.logfile)
            else:
                args.input_files = [args.logfile]
            logfile = defaultlogfile
        else:
            logfile = args.logfile

        # Need to print message informing user that we are adding logging and
        # to where
        log_update("Adding logging to file: %s" % logfile)
        addLogging = True

    if args.concurrency:
        log_update("Setting concurrency to %i." % args.concurrency[0])
        overrideConcurrency = True
        concurrency = args.concurrency[0]
        if concurrency < 0:
            print "Concurrency has to be a positive value"
            sys.exit(1)

    if len(args.input_files) >= 1:
        input_files = args.input_files
    else:
        input_files = ['-']

    for infile in input_files:
        # Open the input file for reading.
        try:
            if infile == '-':
                blob = sys.stdin.read()
            else:
                blob = open(infile).read()
                if args.edit:
                    tmpfile = tempfile.NamedTemporaryFile(suffix=".tmp",
                                              prefix="taboot-")
                    tmpfile.write(blob)
                    tmpfile.flush()
                    try:
                        EDITOR = os.environ.get('EDITOR', 'emacs')
                        call([EDITOR, tmpfile.name])
                    except OSError, e:
                        call(['vi', tmpfile.name])
                    blob = open(tmpfile.name).read()
                    tmpfile.close()
        except IOError, e:
            print "Failed to read input file '%s'. Are you sure it exists?" \
                  % infile
            sys.exit(1)

        # Print a helpful message when loading the YAML fails
        try:
            ds = [doc for doc in yaml.load_all(blob)]
        except yaml.YAMLError, exc:
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark
                probline = blob.split("\n")[mark.line]
                arrow = " " * mark.column + "^"
                msg = """
Syntax Error while loading YAML script, %s.
The problem is on line %s, column %s.

%s
%s""" % (infile, mark.line + 1, mark.column + 1, probline, arrow)
                print msg
                sys.exit(1)
            else:
                # No problem markers means we have to throw a generic
                # "stuff messed up" type message. Sry bud.
                msg = "Could not parse YAML. Check over %s again." % infile
                raise MalformedYAML(msg)

        # Add/Modify Logging if -L is given
        if addLogging:
            for yamldoc in ds:
                for b in yamldoc:
                    if 'output' in b:
                        b['output'].append({'LogOutput': {'logfile': logfile}})
                    else:
                        b['output'] = [{'LogOutput': {'logfile': logfile}},
                                       'CLIOutput']

        # Add/Modify Concurrency if -C is given
        if overrideConcurrency:
            for yamldoc in ds:
                for b in yamldoc:
                    if 'concurrency' in b:
                        del b['concurrency']
                    b['concurrency'] = concurrency

        # If you're just validating the YAML we don't need to build
        # the data structure.
        if args.checkonly:
            continue

        # Remove the actual preflight elements if -s is given
        if args.skippreflight:
            for yamldoc in ds:
                for b in yamldoc:
                    if 'preflight' in b:
                        del b['preflight']

        # Verification that concurrent and non-concurrent features are both
        # not in use.  This is a hack to get the sleep.WaitOnInput (pause) 
        # feature up and running, when our new tabootScript class is in place
        # this check should be handled in validateScript and the task classes
        # should be updated to have a flag that indicates if it is safe for
        # concurrency
        concurrency = False
        nonconcurrenttask = False
        for yamldoc in ds:
            for b in yamldoc:
                if 'concurrency' in b:
                   concurrency = True
                for task in b['tasks']:
                   if task == 'sleep.WaitOnInput':
                      nonconcurrenttask = True
        if concurrency == True and nonconcurrenttask == True:
            msg="""Concurrency is set and a Non-Concurrent task is present.
Please choose one of these options:
1) Use Concurrency and ignore sleep.WaitOnInput
2) Use sleep.WaitOnInput and ignore Concurrency
3) exit\n"""
            response = raw_input(msg)
            if response == "1":
                # remove sleep.WaitOnInput
                for yamldoc in ds:
                    for b in yamldoc:
                        if 'sleep.WaitOnInput' in b['tasks']:
                           b['tasks'].remove('sleep.WaitOnInput')
            elif response == "2":
                for yamldoc in ds:
                    for b in yamldoc:
                        if 'concurrency' in b:
                            del b['concurrency']
            else:
               exit()

        # Print output only if -p is given
        if args.printonly:
            for yamldoc in ds:
                print "---"
                print yaml.dump(yamldoc)
            continue

        # Run each YAML document returned from yaml.load_all
        for yamldoc in ds:
            for runner_source in yamldoc:
                runner = build_runner(runner_source)
                if not runner.run():
                    break

if __name__ == '__main__':
    main()
