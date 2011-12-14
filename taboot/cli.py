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
import taboot
from subprocess import call
from errors import TabootTaskNotFoundException
from taboot import __version__
from tabootScript import TabootScript, ConcurrencyException
from util import resolve_types, log_update, instantiator


def make_blob_copy(blob):
    header = open(taboot.edit_header).read()
    tmpfile = tempfile.NamedTemporaryFile(suffix=".yaml",
                                          prefix="taboot-")
    header = header.replace("$TMPFILE$", tmpfile.name)
    tmpfile.write(header)
    tmpfile.write(blob)
    tmpfile.flush()
    return tmpfile


def sync_blob_copy(tmpfile):
    """
    For backwards compatibility we copy the blob back manually to
    tmpfile. NamedTemporaryFile didn't support the 'delete' parameter
    until py2.6.
    """
    blob = open(tmpfile.name).read()
    tmpname = tmpfile.name
    tmpfile.close()  # The file is erased when close()'d
    open(tmpname, 'w').write(blob)
    return blob


class MalformedYAML(Exception):
    pass


def print_scripts(scripts):
    for script in scripts:
        print script
    sys.exit(0)


def validate_scripts(scripts):
    """
    Validate that all tasks can be located before start. Also check
    that all required elements are present.
    """
    valid = True
    unknown_tasks = []
    missing_elements = []
    for script in scripts:
        try:
            for task in script.getPreflightTypes():
                instantiator(task, 'taboot.tasks', host="*")
            for task in script.getTaskTypes():
                instantiator(task, 'taboot.tasks', host="*")
        except TabootTaskNotFoundException as e:
            valid = False
            unknown_tasks.append(e.args)
        except KeyError as e:
            valid = False
            missing_elements.append(e.args)

    if not valid:
        print "Error: could not parse one of the YAML documents"
        if not unknown_tasks == []:
            print "The following were used but are not valid tasks:"
            for task in unknown_tasks:
                print "    - %s" % task
        if not missing_elements == []:
            print "The following required elements were not found:"
            for element in missing_elements:
                print "    - %s" % element
        sys.exit(1)


def removeTask(doc, task):
    task = str(task).replace('taboot.tasks.', '').replace('()', '')
    for b in doc:
        t2r = []
        for t in b['tasks']:
            if ((isinstance(t, str)
                 and t == task)
                or (isinstance(t, dict)
                    and task in t)):
                t2r.append(t)
        for t in t2r:
            b['tasks'].remove(t)
    return doc


def removeConcurrency(doc):
    for b in doc:
        if 'concurrency' in b:
            del b['concurrency']
    return doc


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
        # Since we are snarfing the next positional argument after -L,
        # we may accidentally snarf up an input yaml file. Hence the
        # test to see if our value is a .yaml file, and if it is, we
        # will set the logfile to the default and store the yaml file
        # name to add to input_files
        pattern = re.compile(".*ya?ml$", re.IGNORECASE)
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

    if len(args.input_files) >= 1:
        input_files = args.input_files
    else:
        input_files = ['-']

    scripts = []

    ##################################################################
    # This next big block (it's pretty big) is responsible for reading
    # in each piece of input, breaking it down into a logical YAML
    # document, handling the $EDITOR passoff, and finally storing each
    # YAML document in an array ('scripts').
    for infile in input_files:
        # Open the input file for reading.
        try:
            if infile == '-':
                blob = sys.stdin.read()
            else:
                blob = open(infile).read()
                if args.edit:
                    tmpfile = make_blob_copy(blob)
                    # Emacs is default editor, as if that needed be said :)
                    try:
                        EDITOR = os.environ.get('EDITOR', 'emacs')
                        call([EDITOR, tmpfile.name])
                    except OSError, e:
                        # vi is fall-back option, I guess...
                        call(['vi', tmpfile.name])
                    blob = sync_blob_copy(tmpfile)
                    log_update("Taboot edit mode: saved changes in %s" \
                                   % tmpfile.name)
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

        # Still in the document reading loop, now we take the read in
        # document and store each logical YAML document it contains as
        # a TabootScript object in the 'scripts' array.
        for doc in ds:
            try:
                scripts.append(TabootScript(doc, infile, args.edit))
            except ConcurrencyException as e:
                msg = """%s
Please choose one of these options:
1) Use Concurrency and ignore %s
2) Use %s and ignore Concurrency
3) exit\n""" % (e, e.value, e.value)
                response = raw_input(msg)
                if response == "1":
                    ds.append(removeTask(doc, e.value))
                elif response == "2":
                    ds.append(removeConcurrency(doc))
                else:
                    sys.exit(1)

    # End of input reading block
    ##################################################################

    # Apply final result of command line options to scripts
    for script in scripts:
        # Add/Modify Logging if -L is given
        if addLogging:
            script.addLogging(logfile)

        # Add/Modify Concurrency if -C is given
        if args.concurrency:
            script.setConcurrency(args.concurrency[0])

        # Remove the actual preflight elements if -s is given
        if args.skippreflight:
            script.deletePreflight()

    # Failed script validation WILL terminate this release
    validate_scripts(scripts)

    # Just validate the document and then stop processing ('-n')
    if args.checkonly:
        exit()

    # Print output ('-p'), exit() in print_scripts()
    if args.printonly:
        print_scripts(scripts)

    # Execute each (validated) script
    for script in scripts:
        runner = taboot.runner.Runner(script)
        if not runner.run():
            break

if __name__ == '__main__':
    main()
