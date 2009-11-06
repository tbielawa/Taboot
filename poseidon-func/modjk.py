from func.minion.modules import func_module
from modjkapi import JKManagerBalancerObjectFactory

class ModJK(func_module.FuncModule):
    version = "0.0.1"
    api_version = "0.0.1"
    description = "Apache httpd mod_jk API"

    def __init__(self):
        self.jk = JKManagerBalancerObjectFactory('http://localhost/jkmanage?mime=xml')

    def list_balancers(self):
        return self.jk.objects()
