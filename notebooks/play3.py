class A:
    def __init__(self):
        self.a()
        self._k = 6

    def a(self):
        a_func()


class B:
    def __init__(self):
        self.a()
        self._k = 6

    def a(self):
        a_func()


def a_func():
    pass
