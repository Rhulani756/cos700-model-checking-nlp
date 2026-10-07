import sys
from pathlib import Path


def get_app_data_dir() -> Path:
    """Return a stable, writable directory for persistent app data
    (uploaded submissions, etc.), correct in both dev and frozen modes.
    """
    if getattr(sys, "frozen", False):
        # Running inside a PyInstaller bundle. Don't use sys._MEIPASS —
        # that's a temp extraction dir that can be cleaned up between runs.
        # Use a stable, user-writable location instead.
        if sys.platform == "win32":
            base = Path.home() / "AppData" / "Local" / "COS700ModelCheckingNLP"
        elif sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support" / "COS700ModelCheckingNLP"
        else:
            base = Path.home() / ".local" / "share" / "cos700-model-checking-nlp"
        return base
    else:
        # Dev mode: relative to project root, same as before.
        return Path(__file__).resolve().parent.parent / "data"


SUBMISSIONS_ROOT = (get_app_data_dir() / "student_submissions").resolve()
SUBMISSIONS_ROOT.mkdir(parents=True, exist_ok=True)