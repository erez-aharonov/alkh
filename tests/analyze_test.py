import alkh
alkh.analyze()
import pandas as pd


class A:
    k = 8

    def __init__(self):
        b = 8 + self.k
        df = pd.DataFrame({'b': b})
        pass

    @staticmethod
    def run(
            n)\
            -> int:
        a = 5
        b = a + 7 + 5.0
        ll = a + 6.4
        c = a + b + 3
        d = b + c
        k = int(d * 2)
        return k


class B:
    def __init__(self):
        b = 8
        pass

    def run(self):
        a = 5
        b = a + 7 + 5.0
        ll = a + 6.4
        c = a + b + 3
        d = b + c
