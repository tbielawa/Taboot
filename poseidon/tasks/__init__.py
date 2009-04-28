class BaseTask(object):
    """
    Base Task.  All tasks should inherit from this.  It does the
    pretty string representation of a task and allows setting of the
    host attribute.
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
    A Func-based task.  All tasks that utilize Func should inherit
    from this.
    """
    import func.overlord.client
    import func.jobthing
    from poseidon.errors import FuncException as _FuncException

    def _func_run(self, func_command, *args):
        """
        Execute a command via Func.

        :Paramaters:
           - `func_command` String representing func command to run (e.g. 'command.run')
           - `*args` Argument(s) to be used when invoking the func command
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
                raise self._FuncException, "%s: %s" % (result[1], result[2])
            return (True, result)
        except Exception, ex:
            return (False, repr(ex))

    def run(self, runner):
        """
        Run the FuncTask.

        :Parameters:
          - `runner` A :class:`poseidon.runner.TaskRunner` instance
        """
        if not hasattr(self, '_command'):
            raise Exception("You MUST set self._command when instantiating a subclass of FuncTask!")

        result = self._func_run(self._command, self._args)

        if result[0]:
            # command executed successfully as far as "func success"
            return self._process_result(result[1])
        else:
            return TaskResult(self, success=False, output=result[1])

class TaskResult(object):
    """
    An encapsulation of the results of a task.  This is passed to one
    or more instances of output classes (derived from BaseOutput) in
    order to display to the user.
    """

    def __init__(self, task, success=False, output=None):
        if hasattr(task, 'host'):
            self._host = task.host
        self._task = repr(task)
        self._success = success
        self._output = output

    def _gettask(self):
        return self._task

    def _settask(self, t):
        self._task = repr(t)

    def _getsuccess(self):
        return self._success

    def _setsuccess(self, success):
        self._success = success

    def _getoutput(self):
        return self._output

    def _setoutput(self, output):
        self._output = output

    def _gethost(self):
        return self._host

    task = property(_gettask, _settask)
    success = property(_getsuccess, _setsuccess)
    output = property(_getoutput, _setoutput)
    host = property(_gethost)
