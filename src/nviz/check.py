"""
Module to analyze local file paths and return structured information.
"""
import os
from pathlib import Path

def get_path_info(local_path):
    """
    Takes a local path and returns a data structure with details about the path.
    
    Args:
        local_path (str): The local path to analyze.
    
    Returns:
        dict: A dictionary containing the filepath, filename, type (file/dir), extension (if file), hidden status, and filesize.
    """

    path = Path(local_path)
    if not path.exists():
        raise FileNotFoundError(f"The path '{local_path}' does not exist.")
    
    path_info = {
        "filepath": str(path.resolve()),
        "filename": path.name,
        "type": "directory" if path.is_dir() else "file",
        "extension": path.suffix if path.is_file() else None,
        "hidden": path.name.startswith('.'),
        "filesize": path.stat().st_size if path.is_file() else None
    }
    
    return path_info

def find_empty_directories(base_path: str) -> list[str]:
    """
    Recursively finds empty directories starting from the given base path.

    Args:
        base_path (str): The base path to start searching for empty directories.

    Returns:
        list: A list of paths to empty directories.
    """
    empty_dirs = []
    base = Path(base_path)

    if not base.exists() or not base.is_dir():
        raise ValueError(f"The base path '{base_path}' is not a valid directory.")

    for directory_info in (get_path_info(str(p)) for p in base.rglob('*')):
        if directory_info["type"] == "directory" and not any(Path(directory_info["filepath"]).iterdir()):  # Directory is empty
            empty_dirs.append(directory_info["filepath"])

    return empty_dirs