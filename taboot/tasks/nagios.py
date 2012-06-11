# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2009-2011, Red Hat, Inc.
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

from taboot.tasks import BaseTask, TaskResult, FuncTask
import taboot.errors
import sys


class NagiosBase(FuncTask):
    """
    All subsequent Nagios tasks are subclasses of this.

    Code note: Because a `FuncTask` expects to make connections to
    `self.host` we need to switch `nagios_url` with `self.host` and
    pass the original `self.host` as an argument.

    .. versionchanged:: 0.2.14

       The previous version specified the `nagios_url` parameter as a
       URL. To facilitate transitions we automatically correct URLs
       into hostnames.

       Previously the `service` key was defined as a scalar, like
       "HTTP" or "JBOSS". This version accepts that key as a scalar OR
       as a list and "does the right thing" in each case.
    """

    def _fix_nagios_url(self, nagios_url):
        """
        For backwards compatability we accept a Nagios URL that
        identifies an HTTP resource.

        This method will take a string like http://foo.com/nagios/cmd.cgi
        and return just the hostname component ("foo.com").
        """
        import re
        return re.sub(r'(https?://)([^/]+)(.*)', r'\2', nagios_url)

    def _process_result(self, result):
        t = TaskResult(self)

        if result.startswith("Fail: "):
            t.success = False
        else:
            t.sucess = True
        t.output = result
        return t


class DisableAlerts(NagiosBase):
    """
    Disable alerts for a host on a nagios instance
    """

    def __init__(self, nagios_url, service_host='', **kwargs):
        """
        :Parameters:
          - `nagios_url`: Hostname of the Nagios server.
          - `service_host`: Hostname of the service host. (optional)
        """
        if service_host != '':
            target_host = service_host
        else:
            target_host = kwargs['host']
        kwargs['host'] = self._fix_nagios_url(nagios_url)
        super(DisableAlerts, self).__init__(target_host, **kwargs)
        self._command = 'nagios.disable_host_notifications'


class EnableAlerts(NagiosBase):
    """
    Enable alerts for a host on a nagios instance
    """

    def __init__(self, nagios_url, service_host='', **kwargs):
        """
        :Parameters:
          - `nagios_url`: Hostname of the Nagios server.
          - `service_host`: Hostname of service host. (optional)
        """
        if service_host != '':
            target_host = service_host
        else:
            target_host = kwargs['host']
        kwargs['host'] = self._fix_nagios_url(nagios_url)
        super(EnableAlerts, self).__init__(target_host, **kwargs)
        self._command = 'nagios.enable_host_notifications'


class ScheduleDowntime(NagiosBase):
    """
    Schedule downtime for services on a host in Nagios
    """

    def __init__(self, nagios_url, service_host='', service='HOST', minutes=30, **kwargs):
        """
        :Parameters:
          - `nagios_url`: Hostname of the Nagios server.
          - `service_host`: Hostname of service host. (optional)
          - `service`: Service or list of services to schedule down for.
          - `minutes`: The number of minutes to schedule downtime
            for. Default is 30.
        """
        import types
        if service_host != '':
            target_host = service_host
        else:
            target_host = kwargs['host']
        kwargs['host'] = self._fix_nagios_url(nagios_url)

        if isinstance(service, types.StringTypes):
            service = [service]

        if not isinstance(minutes, types.IntType):
            if isinstance(minutes, types.FloatType):
                minutes = int(minutes)
            else:
                raise TypeError("Invalid data given for minutes.",
                                "Expecting int type.",
                                "Got '%s'." % minutes)

        super(ScheduleDowntime, self).__init__(target_host, service,
                                               minutes, **kwargs)

        if service == 'HOST':
            self._command = "nagios.schedule_host_downtime"
        else:
            self._command = 'nagios.schedule_svc_downtime'

    def _process_result(self, result):
        t = TaskResult(self)
        t.success = True
        for r in result:
            if r.startswith("Fail: "):
                t.success = t.success & False
            else:
                t.sucess = t.success & True
        t.output = "".join(result)
        return t


class SilenceHost(NagiosBase):
    """
    Silence all notifications for a given host
    """

    def __init__(self, nagios_url, service_host='', **kwargs):
        """
        :Parameters:
          - `nagios_url`: Hostname of the Nagios server.
          - `service_host`: Hostname of service host. (optional)
        """
        import types
        if service_host != '':
            target_host = service_host
        else:
            target_host = kwargs['host']
        kwargs['host'] = self._fix_nagios_url(nagios_url)
        super(SilenceHost, self).__init__(target_host, **kwargs)
        self._command = 'nagios.silence_host'

    def _process_result(self, result):
        t = TaskResult(self)
        t.success = True
        for r in result:
            if r.startswith("Fail: "):
                t.success = t.success & False
            else:
                t.sucess = t.success & True
        t.output = "".join(result)
        return t


class UnsilenceHost(NagiosBase):
    """
    Unsilence all notifications for a given host
    """

    def __init__(self, nagios_url, service_host='', **kwargs):
        """
        :Parameters:
          - `nagios_url`: Hostname of the Nagios server.
          - `host`: Hostname of service host. (optional)
        """
        import types
        if service_host != '':
            target_host = service_host
        else:
            target_host = kwargs['host']
        kwargs['host'] = self._fix_nagios_url(nagios_url)
        super(UnsilenceHost, self).__init__(target_host, **kwargs)
        self._command = 'nagios.unsilence_host'

    def _process_result(self, result):
        t = TaskResult(self)
        t.success = True
        for r in result:
            if r.startswith("Fail: "):
                t.success = t.success & False
            else:
                t.sucess = t.success & True
        t.output = "".join(result)
        return t
