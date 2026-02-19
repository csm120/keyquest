import os
import sys


def get_app_dir() -> str:
    """Get the application directory (where .pyw or .exe is located)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
