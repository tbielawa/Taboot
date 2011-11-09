# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2009,2011, Red Hat, Inc.
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

from taboot.tasks.puppet import PuppetTaskResult
import re


class _FileLikeOutputObject(object):
    """
    A file-like parent class.
    """

    import exceptions
    import time as _time
    defaults = None
    starttime = None

    def __init__(self, *args, **kwargs):
        """
        Creates an instance of a file-like object.

        :Parameters:
           - `args`: all non-keyword arguments.
           - `kwargs`: all keyword arguments.
        """
        import ConfigParser
        import os.path

        if _FileLikeOutputObject.defaults is None:
            if os.path.expanduser("~/.taboot.conf"):
                _FileLikeOutputObject.defaults = ConfigParser.ConfigParser()
                _FileLikeOutputObject.defaults.read(
                    os.path.expanduser("~/.taboot.conf"))

        # Only set the start time once, not for each logger instance
        if _FileLikeOutputObject.starttime is None:
            import datetime
            _FileLikeOutputObject.starttime = datetime.datetime.today()

        self._pos = 0L
        self._closed = False
        self._setup(*args, **kwargs)

    def _setup(self, *args, **kwargs):
        """
        Implementation specific setup.

        :Parameters:
           - `args`: all non-keyword arguments.
           - `kwargs`: all keyword arguments.
        """
        pass

    def flush(self):
        """
        We are not buffering so we always just return None.
        """
        return None

    def read(self, *args, **kwargs):
        """
        We are an output only file-like object. Raise exception.

        :Parameters:
           - `args`: all non-keyword arguments.
           - `kwargs`: all keyword arguments.
        """
        raise self.exceptions.NotImplementedError('Object for output only.')

    def tell(self):
        """
        Returns the position of the file-like object.
        """
        return self._pos

    def truncate(self, size):
        """
        We are an output only file-like object. Raise exception.

        :Parameters:
           - `size`: size to truncate to.
        """
        raise self.exceptions.NotImplementedError(
            'This does not support truncate.')

    def writelines(self, sequence):
        """
        Writes a sequence of lines.

        :Parameters:
           - `sequence`: iterable sequence of data to write.
        """
        for item in sequence:
            self.write(item)

    def write(self, item):
        """
        Writer wrapper (not rapper, beav). Simply calls _write which is
        implementation specific and updates the position.

        :Parameters:
           - `item`: the item to write.
        """
        self._write(item)
        self._pos += 1

    def _write(self, item):
        """
        Implementation of writing data.

        :Parameters:
           - `item`: the item to write.
        """
        raise self.exceptions.NotImplementedError(
            '_write must be overriden.')

    def close(self):
        """
        Close wrapper (again, not rapper, beav). Simply calls _close  which
        is implementation specific and updates the closed property.
        """
        self._close()
        self._closed = True

    def _close(self):
        """
        Implementation of closing the file-like object.
        By default nothing occurs.
        """
        pass

    # Read aliases
    readline = read
    readlines = read
    xreadlines = read
    seek = read

    # Read-only Properties
    closed = property(lambda self: self._closed)
    timestamp = property(lambda self: self._time.strftime(
            "%Y-%m-%d %H:%M:%S", self._time.localtime()))


class CLIOutput(_FileLikeOutputObject):
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
        import Colors
        import sys
        self._c = Colors.Colors()
        self._sys = sys
        self._sys.stdout.write('%s:\n' % (
            self._c.format_string(host, 'blue')))
        self._sys.stdout.write('%s Starting Task[%s]\n' % (
            self.timestamp, self._c.format_string(task, 'white')))

    def _write(self, result):
        """
        Implementation of writing to the CLI.

        :Parameters:
           - `result`: result object to inspect and write
        """
        import types

        # Set output color
        output_color = 'red'
        if result.success:
            output_color = 'green'

        self._sys.stdout.write("%s:\n" % (
            self._c.format_string(result.host, 'blue')))
        self._sys.stdout.write("%s Finished Task[%s]:\n" % (
            self.timestamp, self._c.format_string(
                result.task, output_color)))

        if isinstance(result, PuppetTaskResult):
            # If result is an instance of PuppetTaskResult,
            # colorize the puppet output
            lines = result.output.splitlines()
            for line in lines:
                if re.match('info:', line):
                    self._sys.stdout.write("%s\n" % self._c.format_string(
                        line.strip(), 'green'))
                elif re.match('notice:', line):
                    self._sys.stdout.write("%s\n" % self._c.format_string(
                        line.strip(), 'blue'))
                elif re.match('warning:', line):
                    self._sys.stdout.write("%s\n" % self._c.format_string(
                        line.strip(), 'yellow'))
                elif re.match('err:', line):
                    self._sys.stdout.write("%s\n" % self._c.format_string(
                        line.strip(), 'red'))
                else:
                    self._sys.stdout.write("%s\n" % self._c.format_string(
                        line.strip(), 'normal'))
        else:
            # Use standard pass/fall coloring for output
            if isinstance(result.output, types.ListType):
                for r in result.output:
                    self._sys.stdout.write("%s\n" % self._c.format_string(
                            r.strip(), output_color))
            else:
                self._sys.stdout.write("%s\n" % self._c.format_string(
                        result.output.strip(), output_color))


class LogOutput(_FileLikeOutputObject):
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

        if isinstance(result.output, types.ListType):
            for r in result.output:
                self._log_fd.write("%s\n\n" % r.strip())
        else:
            self._log_fd.write("%s\n\n" % result.output.strip())


class EmailOutput(_FileLikeOutputObject):
    """
    Output a :class:`taboot.tasks.TaskResult` to a logfile.
    """

    def _setup(self, to_addr, from_addr='taboot@redhat.com'):
        """
        Implementation specific setup for outputting to a log.

        :Parameters:
           - `to_addr`: who to send the email to.
           - `from_addr`: who the email is from.
        """
        try:
            import cStringIO as StringIO
        except ImportError, ie:
            import StringIO
        self._to_addr = to_addr
        self._from_addr = from_addr
        self._buffer = StringIO.StringIO()

    def _write(self, result):
        """
        Implementation of writing out to an email.

        :Parameters:
           - `result`: result object to inspect and write
        """
        if result.success:
            success_str = 'OK'
        else:
            success_str = 'FAIL'

        self._buffer.write("%s: %s" % (task_result.task, success_str))

    def flush(self):
        """
        Flushing sends the email with the buffer.
        """
        import smtplib
        from email.mime.text import MIMEText

        self._buffer.flush()
        msg = self.MIMEText(self._buffer.read())
        msg['Subject'] = task_result.host
        msg['From'] = self._from_addr
        msg['To'] = self._to_addr

        smtp = self.smtplib.SMTP()
        smtp.connect()
        smtp.sendmail(self._from_addr, [self._to_addr], msg.as_string())
        smtp.close()

    def __del__(self):
        """
        If the buffer is not empty before destroying, flush.
        """
        if self._buffer.pos < self._buffer.len:
            self.flush()


class HTMLOutput(_FileLikeOutputObject):
    """
    Output a :class:`taboot.tasks.TaskResult` to the command line
    with pretty formatting and colors.
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
        import Colors
        import sys
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

    def _write(self, result):
        """
        DO IT!
        """
        import types
        import sys

        name = self._fmt_hostname(result.host)

        if result.success:
            success_str = self._c.format_string('OK', 'green')
        else:
            success_str = self._c.format_string('FAIL', 'red')

        self._log_fd.write("<p><tt>%s:\n</tt></p>\n<p><tt>%s "\
                               "Finished Task[%s]: %s</tt></p>\n" %
                           (name, self.timestamp, result.task, success_str))

        if isinstance(result, PuppetTaskResult):
            # If result is an instance of PuppetTaskResult,
            # colorize the puppet output
            lines = result.output.splitlines()
            for line in lines:
                if re.match('info:', line):
                    self._log_fd.write("%s<br />\n" %
                                   self._c.format_string(line.strip(),
                                                         'green'))
                elif re.match('notice:', line):
                    self._log_fd.write("%s<br />\n" %
                                   self._c.format_string(line.strip(),
                                                         'blue'))
                elif re.match('warning:', line):
                    self._log_fd.write("%s<br />\n" %
                                   self._c.format_string(line.strip(),
                                                         'yellow'))
                elif re.match('err:', line):
                    self._log_fd.write("%s<br />\n" %
                                   self._c.format_string(line.strip(),
                                                         'red'))
                else:
                    self._log_fd.write("%s<br />\n" %
                                   line.strip())
            self._log_fd.write("<br /><br />\n")
        else:
            # Use standard pass/fall coloring for output
            if isinstance(result.output, types.ListType):
                for r in result.output:
                    self._log_fd.write("<pre>%s</pre>\n<br /><br />\n" %
                                       r.strip())
            else:
                self._log_fd.write("<pre>%s</pre>\n<br /><br />\n" %
                               result.output.strip())

        self._log_fd.flush()
