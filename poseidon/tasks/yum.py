from poseidon.tasks import command, BaseTask


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

    def __init__(self, packages):
        """
        :Parameters:
          - `packages`: A list of packages to install
        """
        YumBase.__init__(self, packages)
        command.Run.__init__(self, 'yum install -y %s' % self._packages_str)


class Update(YumBase, command.Run):
    """
    Update one or more packages.
    """

    def __init__(self, packages=[]):
        """
        :Parameters:
          - `packages`: A list of packages to update.  If `packages` is empty,
             update all packages on the system.
        """
        YumBase.__init__(self, packages)
        command.Run.__init__(self, 'yum update -y %s' % self._packages_str)


class Remove(YumBase, command.Run):
    """
    Remove one or more packages.
    """

    def __init__(self, packages):
        """
        :Parameters:
          - `packages`: A list of packages to remove.
        """
        YumBase.__init__(self, packages)
        command.Run.__init__(self, 'yum remove -y %s' % self._packages_str)
