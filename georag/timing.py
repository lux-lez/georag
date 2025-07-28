import time

from .utils import strf_time

def timer_start(label:str = "") -> dict:
    '''Stores start time'''
    if label != "": print("Started", label, " ... \r", flush=True, end="")
    return {"t0" : time.time_ns(), "label" : label}

def timer_end(kwargs : dict):
    '''Subtracts end time from start time and prints difference'''
    t1 = time.time_ns()
    t0 = kwargs["t0"]
    dt = t1 - t0
    label = kwargs["label"]
    msg = " ".join(["Finished", label, "in", strf_time(dt), "\t"])
    print(msg)

def timed_func(func, *args, label="", verbose=True, **kwargs):
    '''Runs function and prints execution time'''
    if label == "": label = str(func.__name__)
    t = timer_start(label=label)
    y = func(*args, **kwargs)
    timer_end(t)
    return y    


