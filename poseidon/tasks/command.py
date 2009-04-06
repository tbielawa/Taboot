from poseidon.tasks import FuncTask, TaskResult

class Run(FuncTask):
    def __init__(self, *args):
        super(Run, self).__init__(*args)
        self._command = 'command.run'

    def _process_result(self, result):
        t = TaskResult(self)
        if result[0] == 0:
            t.success = True
        else:
            t.success = False
        t.output = result[1]
        return t
