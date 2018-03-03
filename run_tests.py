import os
import nose
import traceback

if __name__ == "__main__":
    if not os.path.isfile("test_settings.py"):
        os.environ["DIAG_CONFIG_MODULE"]="simoc_server.default_test_settings"
    else:
        os.environ["DIAG_CONFIG_MODULE"]="test_settings"

    nose.main(exit=False)
    from simoc_server.exit_handler import _run_all

    try:
        _run_all()
    except Exception as e:
        traceback.print_exc()
    os._exit(0)