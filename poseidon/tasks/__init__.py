class BaseTask(object):
    """
    Base Task.  All Tasks should inherit from this.
    """
    def __init__(self, *args):
        self._name = str(type(self))
        self._name = self._name[self._name.index("'")+1:self._name.rindex("'")]
        self._args = args

    def __repr__(self):
        return "%s%s" % (self._name, self._args)

    def _sethost(self, host):
        self._host = host
    def _gethost(self):
        if hasattr(self, '_host'):
            return self._host
        else:
            return None

    host = property(_gethost, _sethost)

class FuncTask(BaseTask):
    """
    A Func-based Task
    """
    import func.overlord.client
    import func.jobthing
    from poseidon.errors import FuncException

    def func_run(self, func_command, *args):
        """
        Execute a command via Func.

        :Paramaters:
           - `func_command` String representing func command to run (e.g. 'command.run')
        """
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
            return (True, result)
        except Exception, ex:
            return (False, repr(ex))

    def run(self, runner):
        """
        Run the FuncTask
        """
        if not hasattr(self, '_command'):
            raise Exception("You MUST set self._command when instantiating a subclass of FuncTask!")

        result = self.func_run(self._command, self._args)

        if result[0]:
            # command executed successfully as far as "func success"
            return self._process_result(result[1])
        else:
            return TaskResult(self, success=False, output=result[1])

class TaskResult(object):
    def __init__(self, task, success=False, output=None):
        if hasattr(task, 'host'):
            self._host = task.host
        self._task = repr(task)
        self._success = success
        self._output = output

    def gettask(self):
        return self._task

    def settask(self, t):
        self._task = repr(t)

    def getsuccess(self):
        return self._success

    def setsuccess(self, success):
        self._success = success

    def getoutput(self):
        return self._output

    def setoutput(self, output):
        self._output = output

    def gethost(self):
        return self._host

    task = property(gettask, settask)
    success = property(getsuccess, setsuccess)
    output = property(getoutput, setoutput)
    host = property(gethost)
