from poseidon.dispatch import BaseDispatcher

class BaseTask(object):
    """
    Base Task
    """
    def __init__(self, dispatcher=BaseDispatcher):
        self._dispatcher = dispatcher()
        print "Created task: %s" % self

    def __str__(self):
        return "<%s: %s>" % (self.__class__.__name__, self._dispatcher)

    def __call__(self, *args, **kwargs):
        print "Running task: %s with dispatcher %s" % (self, self._dispatcher)
        return self._dispatcher(self._hosts, args, kwargs)

    def set_hosts(self, hosts):
        self._hosts = hosts
