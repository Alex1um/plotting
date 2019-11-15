import math
import re

names = set(dir(math))
names -= {i for i in names if i[:2] == '__'}
names |= {'x'}


def is_equation(s: str):
    return False if set(re.findall('[a-z]+', s.lower())) - names else True


def make_fun_stable(f, default=None):
    def new_fun(*args, **kwargs):
        nonlocal f, default
        try:
            return f(*args, **kwargs)
        except Exception:
            return default

    return new_fun
