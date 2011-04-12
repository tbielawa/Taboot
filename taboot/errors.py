# Copyright 2011, Red Hat, Inc
#
# This software may be freely redistributed under the terms of the GNU
# general public license version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


class FuncException(Exception):
    """
    Exception raised whenever a func request returns REMOTE_ERROR
    """

    def __repr__(self):
        """
        Pretty printing
        """
        s = "FuncException:\n"
        s += '\n'.join(self.args[0])
        return s

    def __str__(self):
        return repr(self)

class TabootException(Exception):
    """
    Base Taboot Exception
    """
    pass

class TabootMissingKrbTkt(TabootException):
    """
    Exception raised when an action that requires a kerberos ticket
    can't find one ahead of time.
    """
    pass
