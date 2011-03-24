# Copyright 2011, Red Hat, Inc
#
# This software may be freely redistributed under the terms of the GNU
# general public license version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


class _FileLikeOutputObject(object):
    """
    A file-like parent class.
    """

    import exceptions
    import time as _time

    def __init__(self, *args, **kwargs):
        """
        Creates an instance of a file-like object.

        :Parameters:
           - `args`: all non-keyword arguments.
           - `kwargs`: all keyword arguments.
        """
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
    Output a :class:`poseidon.tasks.TaskResult` to the command line
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
        # Set output color
        output_color = 'red'
        if result.success:
            output_color = 'green'

        self._sys.stdout.write("%s:\n" % (
            self._c.format_string(result.host, 'blue')))
        self._sys.stdout.write("%s Finished Task[%s]:\n" % (
            self.timestamp, self._c.format_string(
                result.task, output_color)))
        self._sys.stdout.write("%s\n" % self._c.format_string(
            result.output.strip(), output_color))


class LogOutput(_FileLikeOutputObject):
    """
    Output a :class:`poseidon.tasks.TaskResult` to a logfile.
    """

    def _setup(self, host, task, logfile='poseidon.log'):
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
        if result.success:
            success_str = 'OK'
        else:
            success_str = 'FAIL'

        self._log_fd.write("%s:\n%s Finished Task[%s]: %s\n%s\n\n" % (
            result.host, self.timestamp, result.task, success_str,
            result.output.strip()))


class EmailOutput(_FileLikeOutputObject):
    """
    Output a :class:`poseidon.tasks.TaskResult` to a logfile.
    """

    def _setup(self, to_addr, from_addr='poseidon@redhat.com'):
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
