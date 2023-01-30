def check_if_code_position_a_after_b(a, b):
    if a.line > b.line:
        start_after = True
    elif a.line == b.line:
        if a.column >= b.column:
            start_after = True
        else:
            start_after = False
    else:
        start_after = False
    return start_after


def check_code_range_a_is_within_b(a, b):
    test1 = check_if_code_position_a_after_b(a.start, b.start)
    test2 = check_if_code_position_a_after_b(b.end, a.end)
    return test1 and test2


def check_code_range_a_contains_b(a, b):
    return check_code_range_a_is_within_b(b, a)
