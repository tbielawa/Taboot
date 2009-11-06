from func.minion.modules import func_module
from modjkapi import JKManagerBalancerObjectFactory

class ModJK(func_module.FuncModule):
    version = "0.0.1"
    api_version = "0.0.1"
    description = "Apache httpd mod_jk API"
    jk = JKManagerBalancerObjectFactory('http://localhost/jkmanage?mime=xml')

    def list_balancers(self):
        return [b.name for b in self.jk.objects()]

    def list_workers(self, balancer):
        b = self.jk.get_one(name=balancer)
        return [(w.name, w.host) for w in b.objects()]

    def enable_worker(self, balancer, worker):
        w = self.jk.get_one(name=balancer).get_one(name=worker)
        w.enable(ssl=False)
        return True

    def disable_worker(self, balancer, worker):
        w = self.jk.get_one(name=balancer).get_one(name=worker)
        w.disable(ssl=False)
        return True

    def disable_host(self, host):
        """
        Disable `host` across ALL balancers
        """
        disabled_on = []
        balancers = self.jk.objects()
        for balancer in balancers:
            for worker in balancer.objects():
                if worker.host == host:
                    worker.disable()
                    disabled_on.append('%s-%s' % (balancer.name, worker.name))
        return disabled_on

    def enable_host(self, host):
        """
        Enable `host` across ALL balancers
        """
        enabled_on = []
        balancers = self.jk.objects()
        for balancer in balancers:
            for worker in balancer.objects():
                if worker.host == host:
                    worker.enable()
                    enabled_on.append('%s-%s' % (balancer.name, worker.name))
        return enabled_on

    def register_method_args(self):
        """
        The argument export method
        """
        balancer = {
            'type': 'string',
            'optional': False,
            'description': 'The name of the desired balancer'
            }
        worker = {
            'type': 'string',
            'optional': False,
            'description': 'The name of the desired worker'
            }
        host = {
            'type': 'string',
            'optional': False,
            'description': 'A hostname for a worker'
            }

        return {
                'list_balancers': {
                    'description': 'Get list of balancers'
                    },
                'list_workers': {
                    'args': {
                        'balancer': balancer
                        },
                    'description': 'Get list of workers for a balancer'
                    },
                'enable_worker': {
                    'args': {
                        'balancer': balancer,
                        'worker': worker,
                        },
                    'description': 'Enable a worker in a balancer'
                    },
                'disable_worker': {
                    'args': {
                        'balancer': balancer,
                        'worker': worker,
                        },
                    'description': 'Disable a worker in a balancer'
                    },
                'enable_host': {
                    'args': {
                        'host': host
                        },
                    'description': 'Enable all workers for host across all balancers'
                    },
                'disable_host': {
                    'args': {
                        'host': host
                        },
                    'description': 'Disable all workers for host across all balancers'
                    }
                }

