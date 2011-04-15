# Taboot - Client utility for performing deployments with Func.
# Copyright © 2009,2010, Red Hat, Inc.
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

from taboot.tasks import command


class Run(command.Run):
    """
    Run 'puppetd --test'
    """

    def __init__(self, **kwargs):
        super(Run, self).__init__('puppetd --test --color=false',
                                  **kwargs)


class Enable(command.Run):
    """
    Run 'puppetd --enable'
    """

    def __init__(self, **kwargs):
        super(Enable, self).__init__('puppetd --enable', **kwargs)


class Disable(command.Run):
    """
    Run 'puppetd --disable'

    """

    def __init__(self, **kwargs):
        super(Disable, self).__init__('puppetd --disable', **kwargs)
