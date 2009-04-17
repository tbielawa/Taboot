from poseidon.tasks import command

class Start(command.Run):
    def __init__(self, service):
        super(Start, self).__init__('service %s start' % service)

class Stop(command.Run):
    def __init__(self, service):
        super(Stop, self).__init__('service %s stop' % service)

class Restart(command.Run):
    def __init__(self, service):
        super(Restart, self).__init__('service %s restart' % service)
