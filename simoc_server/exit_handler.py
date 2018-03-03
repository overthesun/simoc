import signal
import sys
import traceback
import os
from functools import partial

exit_handlers = []

def register_exit_handler(func, *args, **kwargs):
    handler_partial = partial(func, *args, **kwargs)
    exit_handlers.append(handler_partial)
    return handler_partial

def remove_exit_handler(func):
    print("removing exit handler")
    exit_handlers.remove(func)

def _run_all():
    print("Exit handler..")
    for handler_partial in exit_handlers:
        try:
            handler_partial()
        except:
            traceback.print_exc()

def _exit_handler(signal, frame):
    _run_all()
    os._exit(0)

uncatchable = ['SIG_DFL','SIGSTOP','SIGKILL']

for sig in [x for x in dir(signal.Signals) if x.startswith("SIG")]:
    if sig not in uncatchable:
        signum = getattr(signal, sig)
        signal.signal(signum, _exit_handler)