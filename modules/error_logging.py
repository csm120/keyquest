import traceback
import os

LOG_FILE = "keyquest_error.log"
_MAX_LOG_BYTES = 2 * 1024 * 1024  # 2 MB


def _rotate_if_needed() -> None:
    """Truncate the log file if it exceeds the size limit."""
    try:
        if os.path.getsize(LOG_FILE) > _MAX_LOG_BYTES:
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.write("=== Log rotated (exceeded 2 MB) ===\n")
    except OSError:
        pass


def log_exception(e: BaseException) -> None:
    """Append an exception traceback to the log file."""
    try:
        _rotate_if_needed()
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("=== Unhandled exception ===\n")
            traceback.print_exc(file=f)
            f.write("\n")
    except Exception:
        pass


def log_message(label: str, message: str, tb_str: str = "") -> None:
    """Append a labelled message to the log file (used by subsystems like dialogs)."""
    try:
        _rotate_if_needed()
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n{'=' * 60}\n")
            f.write(f"{label}\n")
            f.write(f"{message}\n")
            if tb_str:
                f.write(f"Traceback:\n{tb_str}\n")
            f.write(f"{'=' * 60}\n")
    except Exception:
        pass

