import copy

def k(x):
    pass

def f(x, y):
    if x > 10:
        if x > 20 and y:
            if x < 30:
                pass
            else:
                if x > 40:
                    pass
        else:
            if x < 5:  # Impossible to cover True branch of this statement.
                pass
    if x == 60:
        raise ValueError("VALUE_ERROR")

    if x > 70:
        if copy.copy(True):  # Impossible to cover False branch of this statement.
            pass

def g(x):
    for _ in range(x):
        pass
    else:
        pass

    while x < 5:
        x += 1
    else:
        if x > 10:
            if x < 12:
                pass
        else:
            pass

def a(x):
    return x

def b(x):
    if a(x) < 2:
        pass
    elif a(x) > 3:
        pass