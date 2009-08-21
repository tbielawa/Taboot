from poseidon.tasks import BaseTask, TaskResult


class NagiosBase(BaseTask):
    """
    Base task for Nagios-related operations.
    """

    #some constants that map to things Nagios expects to get in the POST.
    #A full list is in the Nagios source, in include/common.h
    NAGIOS_DISABLE = '29'
    NAGIOS_ENABLE = '28'
    NAGIOS_ADD_COMMENT = '1'
    NAGIOS_DELETE_ALL_COMMENTS = '20'
    NAGIOS_SCHEDULE_SERVICE_DOWNTIME = '56'

    def __init__(self, nagios_url, **kwargs):
        """
        :Parameters:
          - `nagios_url`: Full URL to a Nagios command handler.  Something
             like: 'https://foo.example.com/nagios/cgi-bin/cmd.cgi'
        """

        super(NagiosBase, self).__init__(**kwargs)
        self._nagios_url = nagios_url

    def _call_curl(self, post_data):
        """
        Shell out to invoke curl.  Gives us easy negotiate auth.
        """
        import os
        command = 'curl -s -o /dev/null --negotiate -u : -k %s' % (self._nagios_url)
        for k in post_data:
            command += ' -d %s=%s' % (k, post_data[k])

        # this comes back byte-packed and we want the high byte
        exit_code = os.system(command) >> 8
        if exit_code == 0:
            return True
        else:
            raise Exception("Curl failed with status %d" % exit_code)

    def _call_nagios(self, command, extra_opts={}):
        """
        build up the POST call for an enable or disable. Example of
        what nagios expects to get:

        cmd_typ=29&cmd_mod=2&host=xmlserver1.app.stage.redhat.com&
        btnSubmit=Commit
        """

        opts = {}
        opts['host'] = self.host
        opts['cmd_typ'] = command
        opts['cmd_mod'] = '2'
        opts['btnSubmit']='Commit'
        opts.update(extra_opts)
        try:
            self._call_curl(opts)
        except:
            print "Failed call to Nagios for " + self.host
            raise


class EnableAlerts(NagiosBase):
    """
    Enable alerts for a host on a nagios instance
    """

    def run(self, runner):
        self._call_nagios(NagiosBase.NAGIOS_ENABLE)
        self._call_nagios(NagiosBase.NAGIOS_DELETE_ALL_COMMENTS)
        return TaskResult(self, success=True)


class DisableAlerts(NagiosBase):
    """
    Disable alerts for a host on a nagios instance
    """

    def run(self, runner):
        self._call_nagios(NagiosBase.NAGIOS_DISABLE)
        self._call_nagios(NagiosBase.NAGIOS_ADD_COMMENT,
                          {'persistent': 'on',
                           'com_data': '"Notifications disabled by Poseidon"'})
        return TaskResult(self, success=True)


class ScheduleDowntime(NagiosBase):
    """
    Schedule nagios service downtime
    """

    def __init__(self, nagios_url, service, minutes=15, **kwargs):
        """
        :Parameters:
          - `nagios_url`: Full URL to a Nagios command handler.  Something
             like: 'https://foo.example.com/nagios/cgi-bin/cmd.cgi'
          - `service`: The name of the service to be scheduled for downtime.
             Example: HTTP
          - `minutes`: The number of minutes to schedule downtime for
        """
        super(ScheduleDowntime, self).__init__(nagios_url, **kwargs)
        self._minutes = minutes
        self._service = service

    def run(self, runner):
        from datetime import datetime, timedelta
        start_time = datetime.strftime(datetime.now(), "%m-%d-%Y %H:%M:%S")
        end_time = datetime.strftime(datetime.now() +
                                     timedelta(minutes=self._minutes),
                                     "%m-%d-%Y %H:%M:%S")
        self._call_nagios(NagiosBase.NAGIOS_SCHEDULE_SERVICE_DOWNTIME,
                          {'service': self._service,
                           'com_data': '"Downtime scheduled by Poseidon"',
                           'start_time': '"%s"' % start_time,
                           'end_time': '"%s"' % end_time,
                           'fixed': 1
                           })
        return TaskResult(self, success=True)
