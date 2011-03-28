# Copyright 2009-2011 Red Hat, Inc
# John Eckersberg <jeckersb@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import threading


class Runner(object):
    """
    The Runner, responsible for running a taboot job.
    """

    import threading
    import taboot.output

    def __init__(self, hosts, tasks, concurrency=1,
                 output=['CLIOutput'],
                 expand_globs=True):
        """
        :Parameters:
           - `hosts`: a List of Func-compatible host globs to operate on.
           - `tasks`: a List of tasks to execute.  Each item in this list must
             be a dict of the following format:
               - Required key named `type`.  This must be a instantiable type.
               - Optional key named `args`.  This is expanded as the positional
                 arguments when instantiating `type`. If not present, the empty
                 tuple `()` is assumed.  If `args` is not a tuple, it is
                 assumed that the value of `args` should be the only item
                 contained within a 1-tuple and is treated as such.
               - Optional key named `kwargs`.  This is exapanded as the keyword
                 arguments when instantiating `type`.  If kwargs is not
                 defined, it is assumed to be the empty dict `{}`.
           - `concurrency`: the number of hosts on which to operate on
             simultaneously.
           - `output`: a list following the same format as `tasks`, containing
             types (and possibly arguments) used for output
           - `expand_globs`: whether to expand the globs or just leave them as
             is.
        """
        self._hosts = hosts
        self._tasks = tasks
        self._concurrency = concurrency
        self._output = output
        self._task_q = []
        if expand_globs:
            self._hosts = self._expand_globs()
        else:
            self._hosts = hosts
        self._semaphore = self.threading.Semaphore(self._concurrency)
        self._fail_event = self.threading.Event()

    def run(self):
        """
        Run the job.
        """
        import signal

        for host in self._hosts:
            t = TaskRunner(host, self._tasks, self._semaphore, self._output,
                           self._fail_event)
            t.start()
            self._task_q.append(t)

        signal.signal(signal.SIGINT, self.__sighandler)

        for task in self._task_q:
            while task.isAlive():
                task.join(0.1)

        if self._fail_event.isSet():
            return False
        return True

    def _expand_globs(self):
        """
        Returns the hosts that expand out from globs.
        """

        import func.overlord.client as fc

        if not self._hosts:
            return []
        if isinstance(self._hosts, basestring):
            glob = self._hosts
        else:
            glob = ';'.join(self._hosts)
        c = fc.Client(glob)
        return c.list_minions()

    def __sighandler(self, signal, frame):
        """
        If we get SIGINT on the CLI, we need to quit all the threads
        in our process group
        """
        import os
        import signal

        os.killpg(os.getpgid(0), signal.SIGQUIT)


class TaskRunner(threading.Thread):
    """
    TaskRunner is responsible for executing a set of tasks for a
    single host in it's own thread.
    """

    from taboot.tasks import TaskResult as _TaskResult

    def __init__(self, host, tasks, semaphore, output, fail_event):
        """
        :Parameters:
          - `host`: The host to operate on.
          - `tasks`: A list of tasks to perform (see :class:`Runner`)
          - `semaphore`: The :class:`Runner` semaphore to acquire before
            executing
          - `output`: A list of outputters to use. (see :class:`Runner`)
          - `fail_event`: The :class:`Runner` failure event to check before
            executing.  If this event is set when the TaskRunner acquires the
            semaphore, then the TaskRunner is effectively a no-op.
        """

        threading.Thread.__init__(self)
        self._host = host
        self._tasks = tasks
        self._semaphore = semaphore
        self._output = output
        self._fail_event = fail_event
        self._state = {}

    def __getitem__(self, key):
        return self._state[key]

    def __setitem__(self, key, value):
        self._state[key] = value

    def run(self):
        """
        Run the task(s) for the given host.  If the fail_event passed
        from the invoking :class:`Runner` is set, do nothing.
        """

        self._semaphore.acquire()

        if self._fail_event.isSet():
            # some other host has bombed
            self._semaphore.release()
            return

        try:
            host_success = True
            for task in self._tasks:
                result = self.run_task(task)
                if not result.success and not result.ignore_errors:
                    host_success = False
                    break
        except:
            self._bail_failure()
            raise

        if not host_success:
            self._bail_failure()
        else:
            self._semaphore.release()
            return host_success

    def _bail_failure(self):
        """
        Die nicely :)
        """

        self._fail_event.set()
        self._semaphore.release()

    def run_task(self, task):
        """
        Run a single task.  Sets task.host and then invokes the run
        method for the task.

        :Parameters:
          - `task`: The task to run
        """

        ignore_errors = False
        if 'ignore_errors' in task:
            if task['ignore_errors'] in ('True', 'true', 1):
                ignore_errors = True

        task = self.__instantiator(task, 'taboot.tasks', host=self._host)

        outputters = []
        for o in self._output:
            instance = self.__instantiator(o, 'taboot.output', host=self._host, task=task)
            outputters.append(instance)

        try:
            result = task.run(self)
        except Exception, e:
            result = self._TaskResult(task, output=repr(e))

        for o in outputters:
            o.write(result)

        result.ignore_errors = ignore_errors
        return result

    def __instantiator(self, type_blob, relative_to, **kwargs):
        """
        Instantiate a type, which is defined by a type blob in the
        following format:

          - If no paremeters are required for the type, then the blob
            should be a single string describing thd desired type

          - If parameters are required, then the type blob must be a
            dictionary with only one key that is a string describing
            the desired type.  The value associated with this key
            should be dictionary which maps the parameter:value pairs
            required when instantiating the type.

        Returns the instantiated object.
        """

        __import__(relative_to)

        def str2type(s):
            import sys
            tokens = s.split('.')
            if len(tokens) == 1:
                return getattr(sys.modules[relative_to], tokens[0])
            else:
                pkg = "%s.%s" % (relative_to, tokens[0])
                __import__(pkg)
                return getattr(sys.modules[pkg], tokens[1])


        if isinstance(type_blob, basestring):
            instance_type = str2type(type_blob)
        else:
            if len(type_blob.keys()) != 1:
                raise Exception("Number of keys isn't 1")
            instance_type = str2type(type_blob.keys()[0])
            kwargs.update(type_blob[type_blob.keys()[0]])

        try:
            return instance_type(**kwargs)
        except TypeError, e:
            import pprint
            print "Unable to instantiate type %s with the following arguments:"\
                % instance_type
            pprint.pprint(kwargs)
            print "Full backtrace below\n"
            raise
