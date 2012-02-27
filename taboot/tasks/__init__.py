# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2009-2011, Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


class BaseTask(object):
    """
    Base Task.  All tasks should inherit from this.  It does the
    pretty string representation of a task and allows setting of the
    host attribute.
    """

    def __init__(self, *args, **kwargs):
        self._name = str(type(self))
        next = self._name.index("'") + 1
        self._name = self._name[next:self._name.rindex("'")]
        self._args = args
        self.host = kwargs['host']
        self.concurrentFriendly = True

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
          - `success`: Whether the task completed successfully or not (boolean)
          - `output`: Any text output produced by the task (string)
        """

        if hasattr(task, 'host'):
            self._host = task.host
        self._task = repr(task)
        self._taskObj = task
        self._success = success
        self._ignore_errors = ignore_errors
        self._formatters = {}

        if isinstance(output, basestring):
            self._output = output
        else:
            raise Exception("Output given to TaskResult must be a string")

    def _gettask(self):
        return self._task

    def _gettaskObj(self):
        return self._taskObj

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

    def format_lines(self, target, colorizer):
        """
        This is the default formatter. Therefore it does not respect
        target or utilize the colorizer.
        """
        if target in self._formatters:
            fmtr = self._formatters[target](self.output, colorizer)
            for l in fmtr._format_lines():
                yield(l)
        else:
            # These are the default formatters. They should probably
            # be broken down into a separate file. it looks bad here.
            if target == "HTMLOutput":
                for line in self.output.splitlines():
                    yield("<pre>%s</pre>\n<br /><br />\n" % line.strip())
            elif target == "CLIOutput":
                output_color = 'red'
                if self.success:
                    output_color = 'green'

                for line in self.output.splitlines():
                    yield("%s\n" % colorizer.format_string(
                            line.strip(), output_color))
            else:
                # Default, just return a stripped string.
                for line in self.output.splitlines():
                    yield("%s\n" % line.strip)

    task = property(_gettask, _settask)
    success = property(_getsuccess, _setsuccess)
    output = property(_getoutput, _setoutput)
    ignore_errors = property(_getignore_errors, _setignore_errors)
    host = property(_gethost)
    taskObj = property(_gettaskObj)
