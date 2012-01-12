# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2009-2012, Red Hat, Inc.
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

import argparse
import datetime
import os
import re
import sys
import taboot
import taboot.runner
import yaml
from taboot import __version__
from taboot import log
from taboot.log import *
from taboot.scripts import Scripts
from taboot.util import parse_int_or_all


def main():
    """
    Main function.
    """

    dt = datetime.datetime.today()
    defaultlogfile = "taboot-%s.log" % (dt.strftime("%Y-%m-%d-%H%M%S"))

    config = {
        "logfile": defaultlogfile,
        "addLogging": False,
        "overrideConcurrency": False,
        "onlypreflight": False,
        "skippreflight": False,
        }

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
    preflight_options = parser.add_mutually_exclusive_group()
    verify_options = parser.add_mutually_exclusive_group()
    preflight_options.add_argument('-s', '--skippreflight',
                        action='store_true', default=False,
                        help='Skip preflight sections if they exist.')
    preflight_options.add_argument('-o', '--onlypreflight',
                        action='store_true', default=False,
                        help='Only run preflight sections.')

    parser.add_argument('-V', '--version', action='version',
                        version='Taboot v%s' % __version__)
    parser.add_argument('-v', '--verbose', action='count',
                        default=1,
                        help='Increase verbosity. Give up to twice.')
    verify_options.add_argument('-n', '--checkonly', action='store_true',
                        default=False,
                        help='Don\'t execute the release, just check \
                              script syntax.')
    verify_options.add_argument('-p', '--printonly', action='store_true',
                        default=False,
                        help='Don\'t execute the release, just check \
                              script syntax and print yaml to stdout.')
    parser.add_argument('-L', '--logfile', const=defaultlogfile, nargs='?',
                        help='Adds a LogOutput type to the \
                              script(s) being run.  If LOGFILE is not \
                              specified then taboot-YYYY-MM-DD-HHMMSS.log \
                              will be used')
    parser.add_argument('-C', '--concurrency', nargs=1, type=parse_int_or_all,
                        help='Set the concurrency for the input script(s). \
                               Give as an integer, or \'all\' for max \
                               concurrency.')
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

    config["onlypreflight"] = args.onlypreflight
    config["skippreflight"] = args.skippreflight
    config["concurrency"] = args.concurrency

    log_debug("Setting verbosity to %s", args.verbose)
    log.LOG_LEVEL_CURRENT = args.verbose

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
        else:
            config["logfile"] = args.logfile

        # Notify we are adding logging and to where
        log_info("Adding logging to file: %s", config["logfile"])
        config["addLogging"] = True

    if len(args.input_files) >= 1:
        input_files = args.input_files
    else:
        input_files = ['-']

    log_debug("Final run-time config values parsed into %s", str(config))
    log_debug("Argparser finished with: %s", str(args))
    scripts = Scripts(input_files, args, config)
    log_debug("Scripts object created with %s YAML documents.",
              len(scripts.scripts))
    valid = scripts.validate_scripts()

    if valid and args.checkonly:
        log_debug("Exiting from dry run. Script verification passed.")
        sys.exit(0)
    elif valid and args.printonly:
        scripts.print_scripts()
        log_debug("Exiting from print only run. Script verification passed.")
        sys.exit(0)
    elif not valid:
        log_debug("Exiting due to invalid scripts.")
        sys.exit(1)
    else:
        log_debug("Executing main run loop in scripts object.")
        if scripts.run():
            sys.exit(0)
        else:
            sys.exit(1)

if __name__ == '__main__':
    main()
