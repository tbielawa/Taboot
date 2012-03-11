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
import taboot.colors.htmlcolors as Colors

class HTMLOutput(taboot.output._FileLikeOutputObject):
    """
    Output a :class:`taboot.tasks.TaskResult` to the command line
    with pretty formatting and colors.

    .. document private functions
    .. automethod:: _write
    """

    logfile_path = None

    def _expand_starttime(self, param):
        """
        Expand any instances of "%s" in `param`
        """
        if '%s' in param:
            p = param % HTMLOutput.starttime
            return p.replace(" ", "-")
        else:
            return param

    def _setup(self, host, task, logfile="taboot-%s.html", destdir="."):
        """
        Implementation specific setup for outputting to an HTML file.

        :Parameters:
           - `host`: name of the host
           - `task`: name of the task
           - `logfile`: name of the file to log to, '%s' is substituted
              with a datestamp
           - `destdir`: directory in which to save the log file to
        """
        import os.path
        import os

        _default_logfile = "taboot-%s.html"
        _default_destdir = "."

        # Pick if the parameter is changed
        # Pick if above is false and logfile is set in defaults
        # Else, use parameter
        if not logfile == _default_logfile:
            _logfile = logfile
        elif HTMLOutput.defaults is not None and \
                HTMLOutput.defaults.has_option("HTMLOutput", "logfile"):
            _logfile = HTMLOutput.defaults.get("HTMLOutput", "logfile")
        else:
            _logfile = logfile

        # Expand %s into a time stamp if necessary
        _logfile = self._expand_starttime(_logfile)

        if not destdir == _default_destdir:
            _destdir = destdir
        elif HTMLOutput.defaults is not None and \
                HTMLOutput.defaults.has_option("HTMLOutput", "destdir"):
            _destdir = HTMLOutput.defaults.get("HTMLOutput", "destdir")
        else:
            _destdir = destdir

        # Figured it all out, now we join them together!
        self._logfile_path = os.path.join(_destdir, _logfile)
        if not os.path.exists(_destdir):
            os.makedirs(_destdir, 0755)

        self._c = Colors.HTMLColors()
        self._log_fd = open(self._logfile_path, 'a')

        # Lets only print this when it is set or changed
        if HTMLOutput.logfile_path is None or \
                not HTMLOutput.logfile_path == self._logfile_path:
            sys.stderr.write("Logging HTML Output to %s\n" % \
                                 self._logfile_path)
            HTMLOutput.logfile_path = self._logfile_path
            sys.stderr.flush()

        # Log the start of this task
        name = self._fmt_anchor(self._fmt_hostname(host))
        start_msg = """<p><tt>%s:</tt></p>
<p><tt>%s Starting Task[%s]\n</tt>""" % (name, self.timestamp, task)
        self._log_fd.write(start_msg)
        self._log_fd.flush()

    def _fmt_anchor(self, text):
        """
        Format an #anchor and a clickable link to it
        """
        h = hash(self.timestamp)
        anchor_str = "<a name='%s' href='#%s'>%s</a>" % (h, h, text)
        return anchor_str

    def _fmt_hostname(self, n):
        """
        Standardize the hostname formatting
        """
        return "<b>%s</b>" % self._c.format_string(n, 'blue')

    def _write_result_header(self, result):
        """
        Write a tasks `result` out to HTML. Handles enhanced stylizing
        for task results that support such as:

        - :py:mod:`taboot.tasks.puppet.PuppetTaskResult`
        - :py:mod:`taboot.tasks.rpm.RPMTaskResult`
        """

        name = self._fmt_hostname(result.host)

        if result.success:
            success_str = self._c.format_string('<b>OK</b>', 'green')
        else:
            success_str = self._c.format_string('<b>FAIL</b>', 'red')

        self._log_fd.write("<p><tt>%s:\n</tt></p>\n<p><tt>%s "\
                               "Finished Task[%s]: %s</tt></p>\n" %
                           (name, self.timestamp, result.task, success_str))

        self._log_fd.flush()

    def _write(self, result):


        self._write_result_header(result)

        for line in result.format_lines(self.__class__.__name__, self._c):
            self._log_fd.write(line)

        self._log_fd.flush()
