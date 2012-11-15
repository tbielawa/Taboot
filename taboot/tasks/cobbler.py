# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2012 Red Hat, Inc.
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

from taboot.tasks import command, TaskResult


class CobblerBase(command.Run):
    """
    Base class for cobbler commands
    """

    def __init__(self, cobbler_url, command, **kwargs):
        kwargs['host'] = cobbler_url
        super(CobblerBase, self).__init__(command, **kwargs)


class Sync(CobblerBase):
    """
    Run 'cobbler sync'

    :Parameters:
      - `cobbler_url`: Hostname of Cobbler Server
    """

    def __init__(self, cobbler_url, **kwargs):
        super(Sync, self).__init__(cobbler_url, 'cobbler sync', **kwargs)

    def _process_result(self, result):
        t = TaskResult(self)
        t.output = result[1].splitlines()[-1]

        import re
        if re.search("COMPLETE", t.output):
            t.success = True
        else:
            t.success = False

        return t


class SystemEdit(CobblerBase):
    """
    Base class for cobbler system edit commands
    """

    def __init__(self, cobbler_url, edit_param, sync=False, **kwargs):
        command = 'cobbler system edit ' + ' '.join(edit_param)
        command += ' --name ' + kwargs['host']
        if sync == True:
            command += ' && cobbler sync'
        super(SystemEdit, self).__init__(cobbler_url, command, **kwargs)


class DisableNetboot(SystemEdit):
    """
    Disable netboot

    :Parameters:
      - `cobbler_url`: Hostname of Cobbler Server

    :Optional Parameters:
      - `sync`: Boolean. Run sync immediately after edit or not
    """

    def __init__(self, cobbler_url, sync=False, **kwargs):
        edit_param = ['--netboot', 'false']
        super(DisableNetboot, self).__init__(cobbler_url, edit_param, sync,
                                             **kwargs)


class EnableNetboot(SystemEdit):
    """
    Enable netboot

    :Parameters:
      - `cobbler_url`: Hostname of Cobbler Server

    :Optional Parameters:
      - `sync`: Boolean. Run sync immediately after edit or not
    """

    def __init__(self, cobbler_url, sync=False, **kwargs):
        edit_param = ['--netboot', 'true']
        super(EnableNetboot, self).__init__(cobbler_url, edit_param, sync,
                                            **kwargs)
