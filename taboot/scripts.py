# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2011, Red Hat, Inc.
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

import taboot.util
import taboot.runner
import sys
import os
import yaml
from tabootScript import TabootScript
from taboot.log import *
from errors import TabootMalformedYAMLException
from subprocess import call


class Scripts(object):
    """
    A collection of TabootScripts.
    """

    def __init__(self, input_files, args, config):
        self.input_files = input_files
        self.args = args
        self.config = config
        self.scripts = []
        self._process_input_files()

    def _process_input_files(self):
        for infile in self.input_files:
            log_debug("Processing input file: %s", infile)
            self._process_input_file(infile)

        for script in self.scripts:
            # Add/Modify Logging if -L is given
            if self.config["addLogging"]:
                script.addLogging(self.config["logfile"])

            # Add/Modify Concurrency if -C is given
            if self.args.concurrency:
                script.setConcurrency(self.args.concurrency[0])

            # Remove the actual preflight elements if -s is given
            if self.args.skippreflight:
                script.deletePreflight()

            script.validate()

    def _process_input_file(self, infile):
        for infile in self.input_files:
            try:
                if infile == '-':
                    blob = sys.stdin.read()
                else:
                    blob = open(infile).read()
                    if self.args.edit:
                        blob = self._edit_input_file(blob)
            except IOError, e:
                log_error("Failed to read input file '%s'. \
Are you sure it exists?", infile)
                sys.exit(1)

            ds = self._load_all_from_yaml(blob, infile)

            # Take the read in document and store each of its logical
            # YAML documents as a TabootScript
            for doc in ds:
                self._add_taboot_script(doc, infile)

    def _load_all_from_yaml(self, blob, infile):
        try:
            ds = [doc for doc in yaml.load_all(blob)]
        except yaml.YAMLError, exc:
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark
                probline = blob.split("\n")[mark.line]
                arrow = " " * mark.column + "^"
                msg = """Syntax Error while loading YAML script, %s.
The problem is on line %s, column %s.

%s
%s"""
                log_error(msg, infile, mark.line + 1, mark.column + 1, probline, arrow)
                sys.exit(1)
            else:
                # No problem markers means we have to throw a generic
                # "stuff messed up" type message. Sry bud.
                msg = "Could not parse YAML. Check over %s again." % infile
                raise TabootMalformedYAMLException(msg)
        return ds

    def _edit_input_file(self, blob):
        """
        Edit the blob given
        """
        tmpfile = taboot.util.make_blob_copy(blob)

        try:
            EDITOR = os.environ.get('EDITOR', 'emacs')
            call([EDITOR, "-nw", tmpfile.name])
        except OSError, e:
            call(['vi', tmpfile.name])

        blob = taboot.util.sync_blob_copy(tmpfile)
        log_info("Taboot edit mode: saved changes in %s", tmpfile.name)
        return blob

    def _add_taboot_script(self, ds, infile):
        taboot_script = TabootScript(ds, infile, self.args.edit)
        self.scripts.append(taboot_script)

        try:
            taboot_script.validate_concurrency()
        except ConcurrencyException as e:
            msg = """%s
Please choose one of these options:
1) Use Concurrency and ignore %s
2) Use %s and ignore Concurrency
3) exit\n""" % (e, e.value, e.value)

            response = raw_input(msg)

            if response == "1":
                taboot_script.removeTask(e.value)
            elif response == "2":
                taboot_script.removeConcurrency()
            else:
                sys.exit(1)

    def print_scripts(self):
        for script in self.scripts:
            print script

    def run(self):
        # Execute each (validated) script
        for script in self.scripts:
            runner = taboot.runner.Runner(script)
            if not runner.run():
                break
