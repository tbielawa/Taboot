# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2009-2012, Red Hat, Inc.
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

import threading
from taboot.util import instantiator
from log import *


class Runner(object):
    """
    The Runner, responsible for running a taboot job.
    """

    import threading
    import taboot.output

    def __init__(self, script, config, expand_globs=True):
        """
        :Parameters:
           - `script`: an instance of tabootScript

           - `expand_globs`: whether to expand the globs or just leave
             them as is.
        """
        self._config = config
        self._hosts = script.getHosts()
        self._tasks = script.getTaskTypes()
        self._output = script.getOutputTypes()
        self._task_q = []
        self._fail_event = self.threading.Event()

        if expand_globs:
            self._hosts = self._expand_globs()
        log_debug("Will operate on %s host(s).", len(self._hosts))

        # Prefight threading
        self._preflight_tasks = script.getPreflightTypes()
        self._preflight_semaphore = self.threading.Semaphore(
                                         len(self._hosts))
        self._preflight_tasks_q = []

        # Main task-body threading
        if script.getConcurrency() == "all":
            self._concurrency = len(self._hosts)
        else:
            self._concurrency = int(script.getConcurrency())
        log_debug("Setting task-body concurrency to %s.",
                  self._concurrency)
        self._semaphore = self.threading.Semaphore(self._concurrency)

    def _run_preflight(self):
        """
        Run the jobs in a prefilght section.
        """
        import signal

        rdy_msg = "\nPre-Flight complete, press enter to continue: "

        for host in self._hosts:
            t = TaskRunner(host, self._preflight_tasks,
                           self._preflight_semaphore,
                           self._output, self._fail_event)
            t.start()
            self._preflight_tasks_q.append(t)

        signal.signal(signal.SIGINT, self.__sighandler)

        for task in self._task_q:
            while task.isAlive():
                task.join(0.1)

        while len(self.threading.enumerate()) > 1:
            # Even though all the threads may have been joined we
            # should still wait for them to terminate. If we don't
            # wait for that we will likely see the 'continue?' prompt
            # before the preflight output gets a chance to print.
            pass

        if not self._config["onlypreflight"]:
            ready = raw_input(rdy_msg)

        if self._fail_event.isSet():
            return False
        return True

    def _run_tasks(self):
        """
        Run a task body.
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

    def run(self):
        """
        Run the preflight/tasks-body
        """

        if len(self._preflight_tasks) > 0:
            if not self._run_preflight():
                return False

        if self._config["onlypreflight"]:
            return True
        else:
            return self._run_tasks()

    def _expand_globs(self):
        """
        Returns the hosts that expand out from globs.

        This is kind of a dirty hack around how Func returns minions
        in an arbitrary order.
        """

        import func.overlord.client as fc

        if not self._hosts:
            return []
        if isinstance(self._hosts, basestring):
            glob = self._hosts
            c = fc.Client(glob)
            return c.list_minions()
        else:
            # Iterate over each given item, expand it, and then push
            # it onto our list. But only if it doesn't exist already!
            found_hosts = []
            for h in self._hosts:
                c = fc.Client(h)
                new_hosts = filter(lambda h: h not in found_hosts,
                                   c.list_minions())
                found_hosts.extend(new_hosts)
                # for found_host in c.list_minions():
                #     h = filter
                #     if not found_host in found_hosts:
                #         found_hosts.append(found_host)
            return found_hosts

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

        task = instantiator(task, 'taboot.tasks', host=self._host)

        outputters = []
        for o in self._output:
            instance = instantiator(o, 'taboot.output',
                                           host=self._host,
                                           task=task)
            outputters.append(instance)

        try:
            result = task.run(self)
        except Exception, e:
            result = self._TaskResult(task, output=repr(e))

        for o in outputters:
            o.write(result)

        result.ignore_errors = ignore_errors
        return result
