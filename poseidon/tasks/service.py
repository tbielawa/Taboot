from poseidon.tasks import command


class Start(command.Run):
    """
    Start a service.
    """

    def __init__(self, service):
        super(Start, self).__init__('service %s start' % service)


class Stop(command.Run):
    """
    Stop a service.
    """

    def __init__(self, service):
        super(Stop, self).__init__('service %s stop' % service)


class Restart(command.Run):
    """
    Restart a service.
    """

    def __init__(self, service):
        super(Restart, self).__init__('service %s restart' % service)
