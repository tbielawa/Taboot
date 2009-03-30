class BaseDispatcher(object):
    """
    Run a task.
    """
    def __init__(self):
        pass

    def __str__(self):
        return self.__class__.__name__

    def run(self, hosts):
        """
        """
        print "%s Executing on hosts %s" % (self, hosts)
        return

    def __call__(self, hosts, *args, **kwargs):
        self.run(hosts)


class FuncDispatcher(BaseDispatcher):
    """
    Run a task via Func.
    """
    import func.overlord.client as fc

    def __call__(self, hosts, *args, **kwargs):
        BaseDispatcher.run(self, hosts)
        return self.fc.Client(';'.join(hosts))

class CLIDispatcher(BaseDispatcher):
    """
    Ask something via CLI (confirmation?)
    """

    def prompt(self, question):
        answer = None
        while answer not in [True, False]:
            answer = raw_input("%s [Y/n]: " % question)
            if answer in ['y', 'Y', '']:
                answer = True
            if answer in ['n', 'N']:
                answer = False

        return answer
