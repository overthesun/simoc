import os
import nose


if __name__ == "__main__":
    os.environ["DIAG_CONFIG_MODULE"]="simoc_server.test_settings"

    nose.main()