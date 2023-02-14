import alkh
alkh.analyze()


class A:
    def __init__(self):
        self.a()
        self.b()
        pass

    def a(self):
        self.a()
        self.b()
        a_func()
        pass

    def b(self):
        self.c()
        pass

    @staticmethod
    def c():
        pass


def a_func():
    h = 1
    a = 2
    b = a + 7 + 5.0
    if h > 1:
        ll = a + 6.4
        with 1 as t:
            try:
                for g in [0, 1]:
                    k = f"{ll} {t} {g}"
                    ft = [k1 for k1 in k]
            except ValueError:
                pass
            finally:
                mm = 0
                k = 0
                while mm < 5:
                    mm += 1
                    k = mm
                pass
