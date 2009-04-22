class BaseOutput(object):
    pass

class CLIOutput(BaseOutput):
    def __call__(self, task_result):
        import Colors

        c = Colors.Colors()
        if task_result.success:
            output_color = 'green'
        else:
            output_color = 'red'

        output = "%s:\n" % c.format_string(task_result.host,'blue')
        output += "Task[%s]:\n" %   c.format_string(task_result.task, output_color)
        output += "%s\n" % c.format_string(task_result.output.strip(), output_color)
        print output

class LogOutput(BaseOutput):
    def __init__(self, logfile='poseidon.log'):
        self._logfile = logfile
        self._log_fd = open(logfile, 'w')

    def __call__(self, task_result):
        if task_result.success:
            success_str = 'OK'
        else:
            success_str = 'FAIL'

        output = "%s:\n" % task_result.host
        output += "Task[%s]: %s\n" % (task_result.task, success_str)
        output += "%s\n\n" % task_result.output.strip()
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
