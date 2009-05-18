class BaseOutput(object):
    """
    Base class for all output-related classes.
    """

    import Colors as _Colors
    import time as _time
    _colors = _Colors.Colors()

    def _timestamp(self):
        return self._time.strftime("%Y-%m-%d %H:%M:%S", self._time.localtime())


class CLIOutput(BaseOutput):
    """
    Output a :class:`poseidon.tasks.TaskResult` to the command line
    with pretty formatting and colors.
    """

    def task_start(self, host, task):
        output = '%s:\n' % self._colors.format_string(host, 'blue')
        output += '%s Starting Task[%s]\n' % (self._timestamp(),
                                              self._colors.format_string(task,
                                                                      'white'))
        print output

    def task_result(self, result):
        c = self._Colors.Colors()
        if result.success:
            output_color = 'green'
        else:
            output_color = 'red'

        output = "%s:\n" % c.format_string(result.host, 'blue')
        output += "%s Finished Task[%s]:\n" % (self._timestamp(),
                                               c.format_string(result.task,
                                                               output_color))
        output += "%s\n" % c.format_string(result.output.strip(), output_color)
        print output


class LogOutput(BaseOutput):
    """
    Output a :class:`poseidon.tasks.TaskResult` to a logfile.
    """

    def __init__(self, logfile='poseidon.log'):
        """
        :Parameters:
          - `logfile` The file to write the log to
        """
        self._logfile = logfile
        self._log_fd = open(logfile, 'a')

    def task_start(self, host, task):
        output = '%s:\n' % host
        output += '%s Starting Task[%s]\n\n' % (self._timestamp(),
                                                task)
        self._log_fd.write(output)

    def task_result(self, result):
        if result.success:
            success_str = 'OK'
        else:
            success_str = 'FAIL'

        output = "%s:\n" % result.host
        output += "%s Finished Task[%s]: %s\n" % (self._timestamp(),
                                               result.task, success_str)
        output += "%s\n\n" % result.output.strip()
        self._log_fd.write(output)


# class EmailOutput(BaseOutput):
#     import smtplib
#     from email.mime.text import MIMEText

#     def __init__(self, to_addr, from_addr='poseidon@redhat.com'):
#         self._to_addr = to_addr
#         self._from_addr = from_addr

#     def __call__(self, task_result):
#         if task_result.success:
#             success_str = 'OK'
#         else:
#             success_str = 'FAIL'

#         output = "%s: %s" % (task_result.task, success_str)

#         msg = self.MIMEText(output)
#         msg['Subject'] = task_result.host
#         msg['From'] = self._from_addr
#         msg['To'] = self._to_addr

#         s = self.smtplib.SMTP()
#         s.connect()
#         s.sendmail(self._from_addr, [self._to_addr], msg.as_string())
#         s.close()
