import pandas as pd

a = 10


def something():
    df = pd.DataFrame({'k': [1, 2], 'l': [2, 6]})
    return something_else(df)


def something_else(df):
    c = a + 5
    return c


d = something()
pass
