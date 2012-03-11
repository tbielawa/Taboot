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

        self._log_fd.write("%s\n\n" % result.output.strip())
