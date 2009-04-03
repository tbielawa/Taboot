class BaseTask(object):
    """
    Base Task
    """
    def __init__(self):
        print "Created task: %s" % self

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, id(self))

class FuncTask(BaseTask):
    """
    A Func-based Task
    """
    import func.overlord.client
    import func.jobthing
    from poseidon.errors import FuncException

    def __init__(self, *args):
        self._args = args

    def set_host(self, host):
        self._host = host

    def func_run(self, func_command, *args):
        import time
        try:
            client = self.func.overlord.client.Client(self._host, async=True)
            job_id = reduce(lambda x, y: getattr(x, y),
                            func_command.split('.'),
                            client)(*args)
            # poll until the job completes
            (status, result) = (None, None)
            while status != self.func.jobthing.JOB_ID_FINISHED:
                (status, result) = client.job_status(job_id)
                time.sleep(1)
            result = result[self._host]
            if result[0] == 'REMOTE_ERROR':
                raise self.FuncException, "%s: %s" % (result[1], result[2])
            return (True, self._host, result)
        except Exception, ex:
            return (False, self._host, repr(ex))
