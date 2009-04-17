from poseidon.tasks import command, BaseTask

class YumBase(BaseTask):
    def __init__(self, packages):
        if isinstance(packages, list):
            self._packages = packages
            self._packages_str = ' '.join(packages)
        else:
            self._packages = [packages]
            self._packages_str = packages

class Install(YumBase, command.Run):
    def __init__(self, packages):
        YumBase.__init__(self, packages)
        command.Run.__init__(self, 'yum install -y %s' % self._packages_str)

class Update(YumBase, command.Run):
    def __init__(self, packages=[]):
        YumBase.__init__(self, packages)
        command.Run.__init__(self, 'yum update -y %s' % self._packages_str)

class Remove(YumBase, command.Run):
    def __init__(self, packages):
        YumBase.__init__(self, packages)
        command.Run.__init__(self, 'yum remove -y %s' % self._packages_str)

