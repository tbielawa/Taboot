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
