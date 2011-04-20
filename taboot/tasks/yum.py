# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2009, Red Hat, Inc.
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
