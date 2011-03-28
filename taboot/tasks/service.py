# Copyright 2011, Red Hat, Inc
#
# This software may be freely redistributed under the terms of the GNU
# general public license version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from taboot.tasks import command


class Start(command.Run):
    """
    Start a service.
    """

    def __init__(self, service, **kwargs):
        super(Start, self).__init__('service %s start' % service, **kwargs)


class Stop(command.Run):
    """
    Stop a service.
    """

    def __init__(self, service, **kwargs):
        super(Stop, self).__init__('service %s stop' % service, **kwargs)


class Restart(command.Run):
    """
    Restart a service.
    """

    def __init__(self, service, **kwargs):
        super(Restart, self).__init__('service %s restart' % service, **kwargs)
