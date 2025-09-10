import time
from collections.abc import Callable


def _next_time(t0: int, change_ns: int):
    while True:
        t0 += change_ns
        yield t0


def precise_loop(func: Callable[..., None], interval_ms: float, *args, **kwargs):
    timer = _next_time(time.perf_counter_ns(), int(interval_ms * 1e6))
    while True:
        func(*args, **kwargs)

        time.sleep((next(timer) - time.perf_counter_ns()) / 1e9)


def main():
    precise_loop(lambda: print(time.time_ns()), 10)


if __name__ == "__main__":
    main()
