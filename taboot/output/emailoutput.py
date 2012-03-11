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
