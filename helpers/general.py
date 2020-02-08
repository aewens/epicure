from sys import stderr
from functools import wraps
from traceback import format_exc

def eprint(*args, **kwargs):
    print(*args, file=stderr, **kwargs)

def coroutine(func):
    @wraps(func)
    def wrapper_coroutine(*args, **kwargs):
        coro = func(*args, **kwargs)
        coro.__next__()
        return coro

    return wrapper_coroutine

def generator(func):
    @wraps(func)
    @coroutine
    def wrapper_generator(*args, **kwargs):
        try:
            while True:
                yield from func(*args, **kwargs)

        except GeneratorExit:
            pass

    return wrapper_generator

def trap(callback):
    def decorator_trap(func):
        @wraps(func)
        def wrapper_trap(*args, **kwargs):
            try:
                value = func(*args, **kwargs)

            except Exception as e:
                value = None
                callback(format_exc())
                
            return value

        return wrapper_trap

    return decorator_trap
