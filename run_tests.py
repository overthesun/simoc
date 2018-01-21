import os
import nose


if __name__ == "__main__":
    if not os.path.isfile("test_settings.py"):
        os.environ["DIAG_CONFIG_MODULE"]="simoc_server.default_test_settings"
    else:
        os.environ["DIAG_CONFIG_MODULE"]="test_settings"

    nose.main()