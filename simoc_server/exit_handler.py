import signal
import sys
import traceback

exit_handlers = []

def register_exit_handler(func, args=None):
    exit_handlers.append((func, args))


def _exit_handler(signal, frame):
    for exit_handler, args in exit_handlers:
        try:
            if args is None:
                exit_handler()
            else:
                exit_handler(*args)
        except:
            traceback.print_exc()
    sys.exit(0)

signal.signal(signal.SIGINT, _exit_handler)