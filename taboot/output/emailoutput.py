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


class EmailOutput(taboot.output._FileLikeOutputObject):
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
        except ImportError:
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
