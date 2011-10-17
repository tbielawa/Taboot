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


import yaml
from util import resolve_types, instantiator, log_update


class YamlDoc:
    """
    Representation of a Yaml Document
    """
    def __init__(self, yamlDoc):
        self.yamlDoc = yamlDoc

    def getYamlDoc(self):
        return self.yamlDoc

    def __str__(self):
        return ("---\n" + yaml.dump(self.yamlDoc))


class TabootScript(YamlDoc):
    """
    Representation of a Taboot Script
    """
    def validateScript(self):
        # Validate that concurrent and non-concurrent tasks don't exist in the
        # same script.  Still need to finish, need to get concurrency value if
        # it exists, then iterate through to see if there are any non-conurrent
        # tasks in, if so raise a ConcurrencyException, will have to catch in
        # cli.py and I'm thinking that we can offer the user the ability to
        # edit the script to correct
        if self.getConcurrency() > 1:
            for b in self.yamlDoc:
                tasks = resolve_types(b['tasks'], 'taboot.tasks')
                for task in tasks:
                    task = instantiator(task, 'taboot.tasks', host="*")
                    if(task.concurrentFriendly == False):
                        raise ConcurrencyException(task)

        # TODO add additional validation logic and throw exception if invalid
        return True

    def __init__(self, yamlDoc, fileName, edited):
        YamlDoc.__init__(self, yamlDoc)
        self.fileName = fileName
        self.edited = edited
        self.validateScript()

    def deletePreflight(self):
        for b in self.yamlDoc:
            if 'preflight' in b:
                del b['preflight']
        self.validateScript()

    def addLogging(self, logfile):
        for b in self.yamlDoc:
            if 'output' in b:
                b['output'].append({'LogOutput': {'logfile': logfile}})
            else:
                b['output'] = [{'LogOutput': {'logfile': logfile}},
                               'CLIOutput']
        self.validateScript()

    def setConcurrency(self, concurrency):
        for b in self.yamlDoc:
            b['concurrency'] = concurrency
        try:
            log_update("Attempting to set concurrency to: %s" % concurrency)
            self.validateScript()
        except ConcurrencyException as e:
            log_update("Cannot set concurrency: %s" % e)
            self.setConcurrency(1)

    def getConcurrency(self):
        for b in self.yamlDoc:
            if 'concurrency' in b:
                return b['concurrency']
        return 1


class ConcurrencyException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr("Concurrency Set and Non-concurrent task: %s present"
                    % self.value)
