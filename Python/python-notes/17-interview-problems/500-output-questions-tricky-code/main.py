"""Output questions + tricky Python code. Each case asserts the real output."""


def q1():  # mutable default argument
    def f(x, acc=[]):
        acc.append(x)
        return acc
    f(1); f(2)
    return f(3)


def q2():  # late-binding closures
    fs = [lambda: i for i in range(3)]
    return [f() for f in fs]


def q3():  # fix with default arg
    fs = [lambda i=i: i for i in range(3)]
    return [f() for f in fs]


def q4():  # is vs == and small-int cache (use runtime values to avoid constant folding)
    a = int("1000"); b = int("1000")
    return (a == b, a is b)


def q5():  # list multiplication aliasing
    g = [[0] * 2] * 2
    g[0][0] = 9
    return g


def q6():  # += on tuple element
    t = ([1], 2)
    try:
        t[0] += [3]
    except TypeError:
        pass
    return t


def q7():  # finally overrides return
    def f():
        try:
            return "try"
        finally:
            return "finally"
    return f()


def q8():  # dict/set ordering and True == 1
    return {1: "a", True: "b", 1.0: "c"}


def q9():  # generator exhaustion
    g = (x for x in range(3))
    return (list(g), list(g))


def q10():  # chained comparison and tuple truth
    return (1 < 2 < 3, 3 > 2 > 2, bool(()), bool((0,)))


def q11():  # class attribute shared, instance shadows
    class A:
        n = []
        k = 0
    a, b = A(), A()
    a.n.append(1); a.k += 1
    return (b.n, b.k, A.k)


def q12():  # slicing never raises, indexing does
    s = [1, 2, 3]
    try:
        s[10]
    except IndexError:
        return s[10:20]


def q13():  # nonlocal / scope: UnboundLocalError
    x = 1
    def f():
        x += 1
    try:
        f()
    except UnboundLocalError:
        return "UnboundLocalError"


def q14():  # sort stability + key, sorted on str vs int
    return sorted(["b", "A", "a", "B"]), sorted(["b", "A", "a", "B"], key=str.lower)


def q15():  # round (banker's) and float
    return (round(0.5), round(1.5), round(2.5), 0.1 + 0.2 == 0.3)


def q16():  # exception variable deleted after except
    e = "outer"
    try:
        1 / 0
    except ZeroDivisionError as e:
        pass
    try:
        return e
    except NameError:
        return "NameError"


def q17():  # dict mutation while iterating
    d = {"a": 1, "b": 2}
    try:
        for k in d:
            d[k + "x"] = 0
    except RuntimeError as ex:
        return str(ex)


def q18():  # copy vs deepcopy
    import copy
    a = [[1], [2]]
    s, d = a.copy(), copy.deepcopy(a)
    a[0].append(9)
    return (s, d)


EXPECTED = {
    q1: [1, 2, 3], q2: [2, 2, 2], q3: [0, 1, 2], q4: (True, False), q5: [[9, 0], [9, 0]],
    q6: ([1, 3], 2), q7: "finally", q8: {1: "c"}, q9: ([0, 1, 2], []),
    q10: (True, False, False, True), q11: ([1], 0, 0), q12: [], q13: "UnboundLocalError",
    q14: (["A", "B", "a", "b"], ["A", "a", "b", "B"]),
    q15: (0, 2, 2, False), q16: "NameError", q17: "dictionary changed size during iteration",
    q18: ([[1, 9], [2]], [[1], [2]]),
}

if __name__ == "__main__":
    for fn, exp in EXPECTED.items():
        got = fn()
        print(fn.__name__, got)
        assert got == exp, (fn.__name__, got, exp)
    print("all ok")
