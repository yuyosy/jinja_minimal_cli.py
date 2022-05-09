import sys
from pathlib import Path


def resource_path(*args) -> Path:
    base_path = None
    if hasattr(sys, '_MEIPASS'):
        base_path = Path(sys.argv[0]).absolute().parent
    else:
        base_path = Path.cwd()
    return base_path.joinpath(*args)
