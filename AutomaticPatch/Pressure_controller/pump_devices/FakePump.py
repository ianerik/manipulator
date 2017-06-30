__all__ = ['FakePump']


class FakePump(object):

    def __init__(self):
        self.val = 0.
        pass

    def measure(self, port=0):
        return self.val

    def set_pressure(self, port=0):
        pass
