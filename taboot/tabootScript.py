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


import func
import yaml
from runner import Runner
from errors import TabootTaskNotFoundException
from util import resolve_types, instantiator
from log import *


class YamlDoc(object):
    """
    Representation of a Yaml Document
    """
    def __init__(self, yamlDoc):
        self.yamlDoc = yamlDoc[0]

    def getYamlDoc(self):
        return self.yamlDoc

    def __str__(self):
        return ("---\n" + yaml.dump(self.yamlDoc))


class TabootScript(YamlDoc):
    """
    Representation of a Taboot Script
    """
    def __init__(self, yamlDoc, fileName, edited, config):
        """
        - `yamlDoc` - Dictionary representing our Taboot Script
        - `fileName` - YAML file the script in
        - `edited` - If we gave :option:`-E` on the command line
        """
        YamlDoc.__init__(self, yamlDoc)
        self.config = config
        self.fileName = fileName
        self.edited = edited
        self.unknown_tasks = set()
        self.elements_missing = set()
        self.unmatched_globs = set()
        self.valid = True
        self.globs_valid = True

    def validate_concurrency(self):
        """
        Validate that concurrent and non-concurrent tasks don't exist
        in the same script.
        """
        # Still need to finish, need to get concurrency value if it
        # exists, then iterate through to see if there are any
        # non-conurrent tasks in, if so raise a ConcurrencyException,
        # will have to catch in cli.py
        #
        # XX: I'm thinking that we can offer the user the ability to
        # edit the script to correct

        if self.getConcurrency() > 1:
            tasks = self.getTaskTypes()
            for task in tasks:
                task = instantiator(task, 'taboot.tasks', host="*")
                if not task.concurrentFriendly:
                    raise ConcurrencyException(task)

        return True

    def validate(self):
        """
        Verify that all tasks can be located, and all required
        elements are present.
        """
        script = self.yamlDoc
        elements_required = set(["hosts", "tasks"])
        elements_present = script.keys()

        self.elements_missing = elements_required.difference(elements_present)
        self.valid = (self.elements_missing == set())

        try:
            for task in self.getPreflightTypes():
                instantiator(task, host="*")
            for task in self.getTaskTypes():
                instantiator(task, host="*")
        except TabootTaskNotFoundException as e:
            self.valid = False
            self.unknown_tasks.add(e.args)
        except KeyError as e:
            self.valid = False
            self.elements_missing.add(e.args)
        return self.valid

    def validateGlobs(self):
        try:
            r = Runner(self, self.config)
        except func.CommonErrors.Func_Client_Exception as e:
            # Sure would be helpful if this exception told you exactly
            # WHICH names bombed... buuuuut what can you do?
            unmatched = e.value.split("\"")[1]
            self.unmatched_globs.add(unmatched)
            self.globs_valid = False

    def deletePreflight(self):
        if self.hasPreflight():
            del self.yamlDoc['preflight']

    def addLogging(self, logfile):
        if 'output' in self.yamlDoc:
            self.yamlDoc['output'].append(
                           {'LogOutput': {'logfile': logfile}})
        else:
            self.yamlDoc['output'] = [{'LogOutput': {'logfile': logfile}},
                               'CLIOutput']

    def setConcurrency(self, concurrency):
        self.yamlDoc['concurrency'] = concurrency
        try:
            log_info("Attempting to set concurrency to: %s", concurrency)
        except ConcurrencyException as e:
            log_warn("Cannot set concurrency: %s. Falling back to 1.", e)
            self.setConcurrency(1)

    def getConcurrency(self):
        if 'concurrency' in self.yamlDoc:
            return self.yamlDoc['concurrency']
        return 1

    def hasPreflight(self):
        if 'preflight' in self.yamlDoc:
            return True
        else:
            return False

    def getPreflight(self):
        if self.hasPreflight():
            return self.yamlDoc['preflight']
        else:
            return []

    def getPreflightTypes(self):
        return resolve_types(self.getPreflight())

    def getPreflightLength(self):
        return len(self.getPreflight())

    def getTasks(self):
        return self.yamlDoc['tasks']

    def getTaskTypes(self):
        return resolve_types(self.getTasks())

    def getTaskLength(self):
        return len(self.getTasks())

    def getHosts(self):
        return self.yamlDoc['hosts']

    def hasOutput(self):
        if 'output' in self.yamlDoc:
            return True
        else:
            return False

    def getOutput(self):
        if self.hasOutput():
            return self.yamlDoc['output']
        else:
            return ['CLIOutput']

    def getOutputTypes(self):
        return resolve_types(self.getOutput(), 'taboot.output')

    def removeTask(self, task):
        """
        Build up a list of instances of ``task`` that appear in the
        datastructure of our YAML document. Then delete them all.
        """
        doc = self.yamlDoc
        task = str(task).replace('taboot.tasks.', '').replace('()', '')
        for b in doc:
            t2r = []
            for t in b['tasks']:
                if ((isinstance(t, str) and t == task) \
                        or (isinstance(t, dict) and task in t)):
                    t2r.append(t)
            for t in t2r:
                b['tasks'].remove(t)

    def removeConcurrency(self):
        doc = self.yamlDoc
        for b in doc:
            if 'concurrency' in b:
                del b['concurrency']


class ConcurrencyException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr("Concurrency Set and Non-concurrent task: %s present"
                    % self.value)
