import time
from functools import wraps

def timed(func, *args, name="", **kwargs):
    if name == "":
        name = str(func.__name__)
    
    print(f"Running {name}")
    t0 = time.time_ns()
    y = func(*args, **kwargs)
    t1 = time.time_ns()
    dt = (t1 - t0) * 1e-9
    print(f"Finished {name} in {dt} seconds")

    return y 
    