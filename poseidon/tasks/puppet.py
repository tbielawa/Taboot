from poseidon.tasks import command

class Run(command.Run):
    def __init__(self, *args):
        super(Run, self).__init__('puppetd --test')

class Enable(command.Run):
    def __init__(self, *args):
        super(Enable, self).__init__('puppetd --enable')

class Disable(command.Run):
    def __init__(self, *args):
        super(Disable, self).__init__('puppetd --disable')

