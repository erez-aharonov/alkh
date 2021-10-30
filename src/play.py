import pandas as pd

a = 10


def do_something():
    df = pd.DataFrame({'k': [1, 2], 'l': [2, 6]})
    return do_something_else(df)


def do_something_else(df):
    c = a + 5
    return c


d = do_something()
pass
