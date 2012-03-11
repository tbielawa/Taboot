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


class LogOutput(taboot.output._FileLikeOutputObject):
    """
    Output a :class:`taboot.tasks.TaskResult` to a logfile.
    """

    def _setup(self, host, task, logfile='taboot.log'):
        """
        Implementation specific setup for outputting to a log.

        :Parameters:
           - `logfile`: name of the logfile to write to.
        """
        self._logfile = logfile
        if self._logfile in ('-', 'stdout', '1'):
            import sys
            self._log_fd = sys.stdout
        else:
            self._log_fd = open(logfile, 'a')
        self._log_fd.write('%s:\n%s Starting Task[%s]\n\n' % (
            host, self.timestamp, task))

    def _write(self, result):
        """
        Implementation of writing to a log.

        :Parameters:
           - `result`: result object to inspect and write
        """
        import types

        if result.success:
            success_str = 'OK'
        else:
            success_str = 'FAIL'

        self._log_fd.write("%s:\n%s Finished Task[%s]: %s\n" % (
            result.host, self.timestamp, result.task, success_str))

        self._log_fd.write("%s\n\n" % result.output.strip())
