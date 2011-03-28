# Copyright 2011, Red Hat, Inc
#
# This software may be freely redistributed under the terms of the GNU
# general public license version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

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
