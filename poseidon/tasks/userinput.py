from poseidon.tasks import BaseTask, TaskResult


class WaitCLI(BaseTask):
    """
    Display a prompt message to the CLI and wait for user to press
    enter before returning from task.
    """

    def __init__(self, message="Press enter to continue\n", **kwargs):
        """
        :Parameters:
          - `message`: The message to prompt on the CLI
        """
        super(WaitCLI, self).__init__()
        self._message = message

    def run(self, runner):
        raw_input(self._message)
        return TaskResult(self, success=True)
