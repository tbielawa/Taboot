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


import yaml
from util import resolve_types, instantiator, log_update


class YamlDoc(object):
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
            tasks = self.getTaskTypes()
            for task in tasks:
                task = instantiator(task, 'taboot.tasks', host="*")
                if(task.concurrentFriendly == False):
                    raise ConcurrencyException(task)

        # TODO add validation logic to ensure that hosts, tasks are present

        # TODO add additional validation logic and throw exception if invalid
        return True

    def __init__(self, yamlDoc, fileName, edited):
        YamlDoc.__init__(self, yamlDoc)
        self.fileName = fileName
        self.edited = edited
        self.validateScript()

    def deletePreflight(self):
        if self.hasPreflight():
            del self.yamlDoc[0]['preflight']
        self.validateScript()

    def addLogging(self, logfile):
        if 'output' in self.yamlDoc[0]:
            self.yamlDoc[0]['output'].append(
                           {'LogOutput': {'logfile': logfile}})
        else:
            self.yamlDoc[0]['output'] = [{'LogOutput': {'logfile': logfile}},
                               'CLIOutput']
        self.validateScript()

    def setConcurrency(self, concurrency):
        self.yamlDoc[0]['concurrency'] = concurrency
        try:
            log_update("Attempting to set concurrency to: %s" % concurrency)
            self.validateScript()
        except ConcurrencyException as e:
            log_update("Cannot set concurrency: %s" % e)
            self.setConcurrency(1)

    def getConcurrency(self):
        if 'concurrency' in self.yamlDoc[0]:
            return self.yamlDoc[0]['concurrency']
        return 1

    def hasPreflight(self):
        if 'preflight' in self.yamlDoc[0]:
            return True
        else:
            return False

    def getPreflight(self):
        if self.hasPreflight():
            return self.yamlDoc[0]['preflight']
        else:
            return []

    def getPreflightTypes(self):
        return resolve_types(self.getPreflight(), 'taboot.tasks')

    def getPreflightLength(self):
        return len(self.getPreflight())

    def getTasks(self):
        return self.yamlDoc[0]['tasks']

    def getTaskTypes(self):
        return resolve_types(self.getTasks(), 'taboot.tasks')

    def getTaskLength(self):
        return len(self.getTasks())

    def getHosts(self):
        return self.yamlDoc[0]['hosts']

    def hasOutput(self):
        if 'output' in self.yamlDoc[0]:
            return True
        else:
            return False

    def getOutput(self):
        if self.hasOutput():
            return self.yamlDoc[0]['output']
        else:
            return ['CLIOutput']

    def getOutputTypes(self):
        return resolve_types(self.getOutput(), 'taboot.output')


class ConcurrencyException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr("Concurrency Set and Non-concurrent task: %s present"
                    % self.value)
