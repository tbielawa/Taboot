from poseidon.tasks import command

class Run(command.Run):
    """
    Run 'puppetd --test'
    """
    def __init__(self, *args):
        super(Run, self).__init__('puppetd --test > /dev/null')

class Enable(command.Run):
    """
    Run 'puppetd --enable'
    """
    def __init__(self, *args):
        super(Enable, self).__init__('puppetd --enable')

class Disable(command.Run):
    """
    Run 'puppetd --disable'
    """
    def __init__(self, *args):
        super(Disable, self).__init__('puppetd --disable')

