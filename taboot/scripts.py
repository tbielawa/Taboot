# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2012, Red Hat, Inc.
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
from errors import TabootMalformedYAMLException, TabootConcurrencyException
from subprocess import call


class Scripts(object):
    """
    A collection of TabootScripts.

    The important highlights here are the public methods: ``run``,
    ``print_scripts``, ``validate_host_globs``, and ``validate_scripts``.
    """

    def __init__(self, input_files, args, config):
        """
        - ``input_files`` should be a list of file names
        - ``args`` should be the result of an argparser instance
        - ``config`` is a dictionary of config values that aren't in ``args``
        """
        log_debug("Creating script object with scripts from: [%s]",
                  ", ".join(input_files))
        self.input_files = input_files
        self.args = args
        self.config = config
        self.scripts = []
        self._process_input_files()

    def _process_input_files(self):
        for infile in self.input_files:
            self._process_input_file(infile)
            log_debug("Finished processing %s.", infile)

        log_debug("Finished loading and processing input files.")
        for script in self.scripts:
            script.validate()

    def _process_input_file(self, infile):
        """
        From here you move on to:

        - `_edit_input_file`
        - `_load_all_from_yaml`
        - `_add_taboot_script`: This is where concurrency validation
          happens
        """
        log_debug("Processing input_file: %s...", infile)
        try:
            if infile == '-':
                blob = sys.stdin.read()
                log_debug("Reading from standard input.")
            else:
                blob = open(infile).read()
                if self.args.edit:
                    log_debug("Opening %s for editing...", infile)
                    blob = self._edit_input_file(blob, infile)
        except IOError, e:
            log_error("Failed to read input file '%s'. \
Are you sure it exists?", infile)
            sys.exit(1)

        ds = self._load_all_from_yaml(blob, infile)

        # Take the read in document and store each of its logical
        # YAML documents as a TabootScript
        log_debug("Discovered %s YAML documents within %s.", len(ds), infile)
        for doc in ds:
            self._add_taboot_script(doc, infile)

    def _load_all_from_yaml(self, blob, infile):
        """
        Given a blob representing a Taboot Script (in YAML format) we
        attempt to turn it into a native Python data structure using
        the ``yaml.load_all`` method.

        Each blob may contain multiple "logical YAML documents". Which
        is akin to having a compendium of some book series. Separate
        logical documents, joined together in one unit.

        Returns a list representing all the logical YAML documents
        found within the blob read into memory. If the YAML conforms
        to Taboot syntax, this will be a list of dictionaries.
        """
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
                log_error(msg, infile, mark.line + 1,
                          mark.column + 1, probline, arrow)
                sys.exit(1)
            else:
                # No problem markers means we have to throw a generic
                # "stuff messed up" type message. Sry bud.
                msg = "Could not parse YAML. Check over %s again." % infile
                raise TabootMalformedYAMLException(msg)
        return ds

    def _edit_input_file(self, blob, infile):
        """
        Edit the blob given
        """
        (tmpfile, offset) = taboot.util.make_blob_copy(blob)

        try:
            EDITOR = os.environ.get('EDITOR', 'emacs')
            call([EDITOR, "-nw", "+%s" % offset, tmpfile.name])
        except OSError, e:
            call(['vi', tmpfile.name])

        blob = taboot.util.sync_blob_copy(tmpfile)
        log_info("Taboot edit mode: saved changes to %s in %s",
                 infile, tmpfile.name)
        return blob

    def _add_taboot_script(self, ds, infile):
        taboot_script = TabootScript(ds, infile, self.args.edit, self.config)
        self.scripts.append(taboot_script)

        try:
            log_debug("Validating (partial) contents of %s...", infile)
            taboot_script.validate_concurrency()
        except TabootConcurrencyException as e:
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
                log_info("Unexpected input. Aborting.")
                sys.exit(1)
        log_debug("%s passed (partial) concurrency validation.", infile)

    def print_scripts(self):
        for script in self.scripts:
            print script

    def run(self):
        # Last sanity check... host globs all expanded?
        if not self.validate_host_globs():
            return False

        # Execute each (validated) script
        for script in self.scripts:
            runner = taboot.runner.Runner(script, self.config)
            if not runner.run():
                return False

        return True

    def validate_host_globs(self):
        """
        This tells each TabootScript to expand its hostnames from
        globs into full host names. Unlike ``validate_scripts`` we
        tell each TabootScript to run its ``validateGlobs`` method
        now, rather then after they've been loaded in
        ``_process_input_files``.

        This is decoupled from syntax validation because it makes
        testing new scripts much simpler. You don't need to be on ANY
        Func infrastructure to write and test Taboot Scripts. In this
        way Func isn't necessary until the moment right before we go
        to run the scripts.
        """
        valid = True
        log_debug("Filtering for unmatched host globs...")

        for script in self.scripts:
            script.validateGlobs()

        for script in filter(lambda s: not s.globs_valid, self.scripts):
            valid = False
            if not script.unmatched_globs == set():
                log_error("\nUnable to match hostname(s):")
                for h in script.unmatched_globs:
                    log_error("    - %s", h)
        return valid

    def validate_scripts(self):
        """
        After each TabootScript is processed it has its ``verify``
        method ran. In this method we look through all of the
        "verified" TabootScripts and check for anyone who had
        problems.
        """
        valid = True
        log_debug("Filtering for invalid scripts...")
        for script in filter(lambda s: not s.valid, self.scripts):

            valid = False
            log_error("Could not parse %s", script.fileName)
            if not script.unknown_tasks == set():
                log_error("\nThe following were used but are not valid tasks:")
                for task in script.unknown_tasks:
                    log_error("    - %s", task)
            if not script.elements_missing == set():
                log_error("\nThe following required elements were not found:")
                for element in script.elements_missing:
                    log_error("    - %s", element)
        log_debug("Finished filtering invalid scripts.")
        return valid
