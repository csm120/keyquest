import traceback

LOG_FILE = "keyquest_error.log"


def log_exception(e: BaseException) -> None:
    """Append an exception traceback to the log file."""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("=== Unhandled exception ===\n")
            traceback.print_exc(file=f)
            f.write("\n")
    except Exception:
        pass

