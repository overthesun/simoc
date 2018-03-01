import signal
import sys
import traceback

exit_handlers = []

def register_exit_handler(func, args=None):
    exit_handlers.append((func, args))


def _exit_handler(signal, frame):
    print("Exit handler..")
    for exit_handler, args in exit_handlers:
        try:
            if args is None:
                exit_handler()
            else:
                exit_handler(*args)
        except:
            traceback.print_exc()
    sys.exit(0)

uncatchable = ['SIG_DFL','SIGSTOP','SIGKILL']

for sig in [x for x in dir(signal.Signals) if x.startswith("SIG")]:
    if sig not in uncatchable:
        signum = getattr(signal, sig)
        signal.signal(signum, _exit_handler)