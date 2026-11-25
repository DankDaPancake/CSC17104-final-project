"""Chạy notebook tại chỗ (tương đương `jupyter nbconvert --execute --inplace`).

Usage: python scripts/run_nb.py notebooks/02_cleaning.ipynb [...]
"""
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

for p in sys.argv[1:]:
    path = Path(p)
    nb = nbformat.read(path, as_version=4)
    NotebookClient(nb, timeout=1800, kernel_name="python3",
                   resources={"metadata": {"path": str(path.parent)}}).execute()
    nbformat.write(nb, path)
    print("OK", path)
