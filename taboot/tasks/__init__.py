# Copyright 2011, Red Hat, Inc
#
# This software may be freely redistributed under the terms of the GNU
# general public license version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

class BaseTask(object):
    """
    Base Task.  All tasks should inherit from this.  It does the
    pretty string representation of a task and allows setting of the
    host attribute.
    """

    def __init__(self, *args, **kwargs):
        self._name = str(type(self))
        self._name = self._name[self._name.index("'")+1:self._name.rindex("'")]
        self._args = args
        self.host = kwargs['host']

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


    import func.jobthing
    from taboot.errors import FuncException as _FuncException

    def _func_run(self, func_command, *args):
        """
        Execute a command via Func.

        :Paramaters:
           - `func_command` String representing func command to run
              (e.g. 'command.run')
           - `*args` Argument(s) to be used when invoking the func command
        """

        import time
        import func.overlord.client
        try:
            client = func.overlord.client.Client(self._host, async=True)
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
                raise self._FuncException(result[1:])
            return (True, result)
        except Exception, ex:
            return (False, repr(ex))

    def run(self, runner):
        """
        Run the FuncTask.

        :Parameters:
          - `runner` A :class:`taboot.runner.TaskRunner` instance
        """

        if not hasattr(self, '_command'):
            raise Exception("You MUST set self._command when instantiating " +
                            "a subclass of FuncTask!")

        result = self._func_run(self._command, *(self._args))

        if result[0]:
            # command executed successfully as far as "func success"
            return self._process_result(result[1])
        else:
            return TaskResult(self, success=False, output=result[1])


class FuncErrorTask(FuncTask):
    """
    Explicitly cause a func remote error by calling a bad command.
    Used to verify func exception handling works as expected
    """

    def __init__(self, *args, **kwargs):
        super(FuncErrorTask, self).__init__(*args, **kwargs)
        self._command = 'thiscommand.DoesntExist'


class TaskResult(object):
    """
    An encapsulation of the results of a task.  This is passed to one
    or more instances of output classes (derived from BaseOutput) in
    order to display to the user.
    """

    def __init__(self, task, success=False, output='', ignore_errors=False):
        """
        :Parameters:
          - `task`: The task object represented by this result
          - `success`: Whether the task completed successfully or not
          - `output`: Any text output produced by the task
        """

        if hasattr(task, 'host'):
            self._host = task.host
        self._task = repr(task)
        self._success = success
        self._output = output
        self._ignore_errors = ignore_errors

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

    def _getignore_errors(self):
        return self._ignore_errors

    def _setignore_errors(self, ignore_errors):
        self._ignore_errors = ignore_errors

    def _gethost(self):
        return self._host

    task = property(_gettask, _settask)
    success = property(_getsuccess, _setsuccess)
    output = property(_getoutput, _setoutput)
    ignore_errors = property(_getignore_errors, _setignore_errors)
    host = property(_gethost)
