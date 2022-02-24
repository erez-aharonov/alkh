import pandas as pd
from tests import play_imports

a = 10


def do_something():
    df = pd.DataFrame({'k': [1, 2], 'l': [2, 6]})
    return do_something_else(df)


def do_something_else(df):
    c = a + 5
    some_object = play_imports.A()
    some_object.run()
    df_2 = df + c
    return df_2


d = do_something()
pass
