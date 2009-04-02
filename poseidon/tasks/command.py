from poseidon.tasks import FuncTask

class Run(FuncTask):
    def run(self):
        print self.func_run('command.run', self._args)
