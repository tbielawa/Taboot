from poseidon.tasks import FuncTask

class Run(FuncTask):
    def run(self):
        result = self.func_run('command.run', self._args)
        output = "command.Run(%s)\n" % self._args
        if result[0]:
            return (result[0], result[1], output + result[2][1])
        else:
            return (result[0], result[1], output + result[2])
