from poseidon.tasks import BaseTask
from poseidon.dispatch import FuncDispatcher

class Bleed(BaseTask):
    def __init__(self, command, dispatcher=FuncDispatcher):
        self._command = command
        BaseTask.__init__(self, dispatcher)

    def __call__(self, *args, **kwargs):
        print "Running %s:" % self
        results = self._dispatcher(self._hosts).command.run(self._command)
        for host, result in results.iteritems():
            print "%s: " % host,
            if result[0] == 'REMOTE_ERROR':
                print "Error!"
            else:
                print result[1][:-1]
