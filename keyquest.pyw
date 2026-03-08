#!python3.9

import os
import shutil
import subprocess
import sys

if sys.version_info[:2] != (3, 9):
    launcher = shutil.which("pyw") or shutil.which("py")
    if launcher:
        script = os.path.abspath(__file__)
        try:
            subprocess.Popen([launcher, "-3.9", script, *sys.argv[1:]], close_fds=True)
            raise SystemExit(0)
        except Exception:
            pass

if "--version" in sys.argv:
    from modules.version import __version__
    print(__version__)
    sys.exit(0)

try:
    from modules.keyquest_app import main
except Exception as e:
    try:
        from modules import error_logging

        error_logging.log_exception(e)
    except Exception:
        pass
    raise


if __name__ == "__main__":
    main()
