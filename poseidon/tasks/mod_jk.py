from poseidon.tasks import BaseTask, FuncTask, TaskResult

JK_ENABLE = 0
JK_DISABLE = 1

class ToggleHost(FuncTask):
    def __init__(self, action, *args, **kwargs):
        super(ToggleHost, self).__init__(*args, **kwargs)
        self._action = action
        if action == JK_ENABLE:
            self._command = 'poseidon.modjk.enable_host'
        elif action == JK_DISABLE:
            self._command = 'poseidon.modjk.disable_host'
        else:
            raise Exception("Undefined toggle action")

    def _process_result(self, result):
        t = TaskResult(self)
        if len(result) > 0:
            t.success = True
            if self._action == JK_ENABLE:
                verb = 'Enabled'
            else:
                verb = 'Disabled'
            t.output = "%s AJP on the following balancer/worker pairs:\n" % verb
            for balancer,worker in result:
                t.output += "%s:  %s\n" % (balancer, worker)
        else:
            t.success = False
            t.output = "Failed to find worker host"
        return t

class OutOfRotation(BaseTask):
    """
    Remove an AJP node from rotation on a proxy via modjkapi access on
    the proxy with func.
    """

    def __init__(self, *args, **kwargs):
        super(OutOfRotation, self).__init__(*args, **kwargs)

    def run(self, runner):
        output = ""
        success = True
        for proxy in self._args:
            toggler = ToggleHost(JK_DISABLE, self._host, host=proxy)
            result = toggler.run(runner)
            output += "%s:\n" % proxy
            output += "%s\n" % result.output
            if result.success == False:
                success = False
                break
        return TaskResult(self, success=success, output=output)
