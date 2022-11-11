import os
import sys
from glob import glob


def find_files(_path: str, _pattern: str) -> list:
    "Return list of file paths in folder _path matching _pattern."
    return glob(_path + _pattern, recursive=True)


def strip_extension(path: str):
    "Return file path without extension"
    return os.path.splitext(path)[0]
