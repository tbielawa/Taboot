from func.minion.modules import func_module
from modjkapi import JKManagerBalancerObjectFactory

class ModJK(func_module.FuncModule):
    version = "0.0.1"
    api_version = "0.0.1"
    description = "Apache httpd mod_jk API"

    def __init__(self):
        self.jk = JKManagerBalancerObjectFactory('http://localhost/jkmanage?mime=xml')

    def list_balancers(self):
        return [str(b) for b in self.jk.objects()]

    def register_method_args(self):
        """
        The argument export method
        """

        return {
                'list_balancers':{
                    'description':'Get list of balancers'
                    }
                }

