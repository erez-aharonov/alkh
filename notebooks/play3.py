class A:
    def __init__(self):
        self.a()
        self._k = 6

    def a(self):
        a_func()


class B:
    def __init__(self):
        j = self.a()
        self._k = j

    def a(self):
        a_func()
        return 5


def a_func():
    pass
