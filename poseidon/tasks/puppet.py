from poseidon.tasks import command


class Run(command.Run):
    """
    Run 'puppetd --test'
    """

    def __init__(self, *args, **kwargs):
        super(Run, self).__init__('puppetd --test > /dev/null',
                                  **kwargs)


class Enable(command.Run):
    """
    Run 'puppetd --enable'
    """

    def __init__(self, *args, **kwargs):
        super(Enable, self).__init__('puppetd --enable', **kwargs)


class Disable(command.Run):
    """
    Run 'puppetd --disable'

    """

    def __init__(self, *args, **kwargs):
        super(Disable, self).__init__('puppetd --disable', **kwargs)
