import traceback
import os
from modules.app_paths import get_app_dir

LOG_FILE = "keyquest_error.log"
_MAX_LOG_BYTES = 2 * 1024 * 1024  # 2 MB


def get_log_file_path() -> str:
    """Return the full path to the local KeyQuest error log."""
    return os.path.join(get_app_dir(), LOG_FILE)


def touch_log_file() -> str:
    """Ensure the local error log file exists and return its path."""
    path = get_log_file_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "a", encoding="utf-8"):
                pass
    except OSError:
        pass
    return path


def _rotate_if_needed() -> None:
    """Truncate the log file if it exceeds the size limit."""
    try:
        log_path = touch_log_file()
        if os.path.getsize(log_path) > _MAX_LOG_BYTES:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("=== Log rotated (exceeded 2 MB) ===\n")
    except OSError:
        pass


def log_exception(e: BaseException) -> None:
    """Append an exception traceback to the log file."""
    try:
        _rotate_if_needed()
        with open(touch_log_file(), "a", encoding="utf-8") as f:
            f.write("=== Unhandled exception ===\n")
            traceback.print_exc(file=f)
            f.write("\n")
    except Exception:
        pass


def log_message(label: str, message: str, tb_str: str = "") -> None:
    """Append a labelled message to the log file (used by subsystems like dialogs)."""
    try:
        _rotate_if_needed()
        with open(touch_log_file(), "a", encoding="utf-8") as f:
            f.write(f"\n{'=' * 60}\n")
            f.write(f"{label}\n")
            f.write(f"{message}\n")
            if tb_str:
                f.write(f"Traceback:\n{tb_str}\n")
            f.write(f"{'=' * 60}\n")
    except Exception:
        pass


def read_log_tail(max_chars: int = 2000) -> str:
    """Return the tail of the local log for bug-report prefills."""
    try:
        with open(touch_log_file(), "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return ""

    if len(text) <= max_chars:
        return text.strip()
    return text[-max_chars:].strip()
