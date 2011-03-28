from taboot.tasks import BaseTask
from taboot.dispatch import CLIDispatcher


class Ask_CLI(BaseTask):
    """
    Block on CLI Input
    """

    def __init__(self, question, dispatcher=CLIDispatcher):
        self._question = question
        BaseTask.__init__(self, dispatcher)

    def __call__(self, *args, **kwargs):
        print "Running %s:" % self
        result = self._dispatcher.prompt(self._question)
        if result:
            print 'OK'
        else:
            print 'Not OK!'
        return result
