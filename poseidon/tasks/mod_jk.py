from poseidon.tasks import BaseTask, TaskResult


class JKBaseTask(BaseTask):
    from modjkapi import JKManagerBalancerObjectFactory \
        as _JKManagerBalancerObjectFactory

    def __init__(self, proxies, **kwargs):
        """
        :Parameters:
          - `proxies` A list of mod_jk proxy servers to operate on
        """
        super(JKBaseTask, self).__init__(proxies, **kwargs)
        self._proxies = proxies

    def _get_workers(self, jk_host):
        datasource = self._JKManagerBalancerObjectFactory(
                     'http://%s/jkmanage?mime=xml' % jk_host)
        balancers = datasource.objects()

        workers = []
        for balancer in balancers:
            for worker in balancer.workers:
                if worker.host == self.host:
                    workers.append(worker)
        return workers


class OutOfRotation(JKBaseTask):
    """
    Take a host of rotation.
    """

    def run(self, runner):
        result = TaskResult(self)
        output = ''
        for proxy in self._proxies:
            try:
                workers = self._get_workers(proxy)
            except Exception, e:
                result.output = e
                return result

            for worker in workers:
                output += "Stopping worker: %s\n" % worker
                worker.stop(ssl=False)

        result.output = output
        result.success = True
        return result


class InRotation(JKBaseTask):
    """
    Put a host in rotation.
    """

    def run(self, runner):
        result = TaskResult(self)
        proxies = self._args[0]
        output = ''
        for proxy in self._proxies:
            try:
                workers = self._get_workers(proxy)
            except Exception, e:
                result.output = e
                return result

            for worker in workers:
                output += "Enabling worker: %s\n" % worker
                worker.enable(ssl=False)

        result.output = output
        result.success = True
        return result
