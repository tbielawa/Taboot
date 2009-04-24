from poseidon.tasks import BaseTask
import time

class PollTask(BaseTask):
    """
    PollTask.  A task that will poll a particular task until the task
    succeeds or until max_attempts is reached.

    :Parameters:
        - `task` The task to poll.
        - `sleep_interval` The number of seconds to wait before trying 
                           the task again.
        - `max_attempts` The maximum number of attempts that the task 
                         should be run.
        - `fail_task` The task to run when max_attempts has been exhausted.
                      If no fail_task is provided, then a simple TaskResult
                      indicating failure is returned.
    """
    def __init__(self, task, sleep_interval=5, max_attempts=6, fail_task=None):
        super(PollTask, self).__init__()
        self._task = task
        self._task.host = self.host
        self._sleep_interval = sleep_interval
        self._max_attempts = max_attempts
        self._fail_task = fail_task
        self._fail_task.host = self.host

    def run(self):
        for x in range(self._max_attempts): 
            try:
                result = self._task.run()
            except Exception, e:
                result = TaskResult(self._task, output=repr(e))
            if result.success:
                return result
            time.sleep(self._sleep_interval)

        # exhausted max_attempts
        if self._fail_task != None:
            result = self._fail_task.run()
        else:
            # return a "failed" TaskResult, stop executing further tasks
            return TaskResult(self, success=False, 
                    output="Max attempts of %s reached running %s" % (max_attempts, repr(self._task)))
