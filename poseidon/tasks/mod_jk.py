# Copyright 2011, Red Hat, Inc
#
# This software may be freely redistributed under the terms of the GNU
# general public license version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from poseidon.tasks import BaseTask, FuncTask, TaskResult

JK_ENABLE = 0
JK_DISABLE = 1
JK_STOP = 2

class ToggleHost(FuncTask):
    def __init__(self, action, host, **kwargs):
        super(ToggleHost, self).__init__(host, **kwargs)
        self._action = action
        if action == JK_ENABLE:
            self._command = 'poseidon.modjk.enable_host'
        elif action == JK_DISABLE:
            self._command = 'poseidon.modjk.disable_host'
        elif action == JK_STOP:
            self._command = 'poseidon.modjk.stop_host'
        else:
            raise Exception("Undefined toggle action")

    def _process_result(self, result):
        t = TaskResult(self)
        if len(result) > 0:
            t.success = True
            if self._action == JK_ENABLE:
                verb = 'Enabled'
            elif self._action == JK_DISABLE:
                verb = 'Disabled'
            elif self._action == JK_STOP:
                verb = 'Stopped'
            t.output = "%s AJP on the following balancer/worker pairs:\n" % verb
            for balancer,worker in result:
                t.output += "%s:  %s\n" % (balancer, worker)
        else:
            t.success = False
            t.output = "Failed to find worker host"
        return t

class JKBaseTask(BaseTask):
    def __init__(self, proxies, action, **kwargs):
        super(JKBaseTask, self).__init__(**kwargs)
        from sys import modules
        self.proxies = proxies
        self.jkaction = getattr(modules[self.__module__], "JK_%s" % action.upper())

    def run(self, runner):
        output = ""
        success = True
        for proxy in self.proxies:
            toggler = ToggleHost(self.jkaction, self._host, host=proxy)
            result = toggler.run(runner)
            output += "%s:\n" % proxy
            output += "%s\n" % result.output
            if result.success == False:
                success = False
                break
        return TaskResult(self, success=success, output=output)

class OutOfRotation(JKBaseTask):
    """
    Remove an AJP node from rotation on a proxy via modjkapi access on
    the proxy with func.
    """
    def __init__(self, proxies, action="stop", **kwargs):
        super(OutOfRotation, self).__init__(proxies, action, **kwargs)

class InRotation(JKBaseTask):
    """
    Put an AJP node in rotation on a proxy via modjkapi access on
    the proxy with func.
    """
    def __init__(self, proxies, action="enable", **kwargs):
        super(InRotation, self).__init__(proxies, action, **kwargs)

