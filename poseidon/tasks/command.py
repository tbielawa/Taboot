from poseidon.tasks import FuncTask

class Run(FuncTask):
    def run(self):
        result = self.func_run('command.run', self._args)
        return (result[0], result[1], result[2][1])
