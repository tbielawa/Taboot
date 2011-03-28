# Copyright 2011, Red Hat, Inc
#
# This software may be freely redistributed under the terms of the GNU
# general public license version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from taboot.tasks import command, BaseTask


class YumBase(BaseTask):
    """
    Base class for all Yum-related tasks.
    """

    def __init__(self, packages):
        if isinstance(packages, list):
            self._packages = packages
            self._packages_str = ' '.join(packages)
        else:
            self._packages = [packages]
            self._packages_str = packages


class Install(YumBase, command.Run):
    """
    Install one or more packages.
    """

    def __init__(self, packages, **kwargs):
        """
        :Parameters:
          - `packages`: A list of packages to install
        """
        YumBase.__init__(self, packages)
        command.Run.__init__(self, 'yum install -y %s' % self._packages_str,
                             **kwargs)


class Update(YumBase, command.Run):
    """
    Update one or more packages.
    """

    def __init__(self, packages=[], **kwargs):
        """
        :Parameters:
          - `packages`: A list of packages to update.  If `packages` is empty,
             update all packages on the system.
        """
        YumBase.__init__(self, packages)
        command.Run.__init__(self, 'yum update -y %s' % self._packages_str,
                             **kwargs)


class Remove(YumBase, command.Run):
    """
    Remove one or more packages.
    """

    def __init__(self, packages, **kwargs):
        """
        :Parameters:
          - `packages`: A list of packages to remove.
        """
        YumBase.__init__(self, packages)
        command.Run.__init__(self, 'yum remove -y %s' % self._packages_str,
                             **kwargs)
