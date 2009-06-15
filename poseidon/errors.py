class FuncException(Exception):
    def __repr__(self):
        """
        Pretty printing
        """
        s = "FuncException:\n"
        s += '\n'.join(self.args[0])
        return s

    def __str__(self):
        return repr(self)
