import alkh


def do_something(a: int):
    k = do_something_2(a)
    k2 = k + 1
    alkh.take_it_offline('/app/tests', 1)
    return k2


def do_something_2(b: int):
    return b + 1


a_number = do_something(5)
