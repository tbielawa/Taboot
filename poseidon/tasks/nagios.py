from poseidon.tasks import BaseTask, TaskResult


class NagiosBase(BaseTask):
    """
    Base task for Nagios-related operations.
    """

    def __init__(self, nagios_url):
        """
        :Parameters:
          - `nagios_url`: Full URL to a Nagios command handler.  Something
             like: 'http://foo.example.com/nagios/cgi-bin/cmd.cgi'
        """

        import poseidon.contrib.nagios as nagios
        super(NagiosBase, self).__init__()
        self._nagios_url = nagios_url
        self._nagios_handle = nagios.Nagios(self._nagios_url)


class EnableAlerts(NagiosBase):
    """
    Enable alerts for a host on a nagios instance
    """

    def run(self, runner):
        self._nagios_handle.enable_alerts(self.host)
        self._nagios_handle.delete_all_comments(self.host)
        return TaskResult(self, success=True)


class DisableAlerts(NagiosBase):
    """
    Disable alerts for a host on a nagios instance
    """

    def run(self, runner):
        self._nagios_handle.disable_alerts(self.host)
        self._nagios_handle.add_comment(self.host,
                                        'Disabled via Poseidon')
        return TaskResult(self, success=True)
