# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2009,2011-2012 Red Hat, Inc.
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

import taboot.output
import sys
import taboot.colors as Colors

class CLIOutput(taboot.output._FileLikeOutputObject):
    """
    Output a :class:`taboot.tasks.TaskResult` to the command line
    with pretty formatting and colors.
    """

    def _setup(self, host, task):
        """
        Implementation specific setup for outputting to the CLI.

        :Parameters:
           - `host`: name of the host
           - `task`: name of the task
        """
        self._c = Colors.Colors()
        self._sys = sys
        self._sys.stdout.write('%s:\n' % (
            self._c.format_string(host, 'blue')))
        self._sys.stdout.write('%s Starting Task[%s]\n' % (
            self.timestamp, self._c.format_string(task, 'white')))

    def _write_result_header(self, result):
        """
        Implementation of writing to the CLI.

        :Parameters:
           - `result`: result object to inspect and write
        """

        # Set output color
        output_color = 'red'
        if result.success:
            output_color = 'green'

        self._sys.stdout.write("%s:\n" % (
            self._c.format_string(result.host, 'blue')))
        self._sys.stdout.write("%s Finished Task[%s]:\n" % (
            self.timestamp, self._c.format_string(
                result.task, output_color)))

    def _write(self, result):
        self._write_result_header(result)

        for line in result.format_lines(self.__class__.__name__, self._c):
            self._sys.stdout.write(line)

        self._sys.stdout.flush()
