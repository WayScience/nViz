"""
Module to analyze local file paths and return structured information.
"""

import pathlib
from collections import Counter
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Union

paths_type = Dict[str, Union[str, bool, int, float, None]]


def get_path_info(base_path: str, ignore: Optional[List[str]] = None) -> paths_type:
    """
    Takes a local path and returns a data structure with
    details about the path.

    Args:
        base_path (str):
            The local path to analyze.
        ignore (Optional[List[str]]):
            A list of patterns to ignore
            (e.g., hidden files, specific file types).

    Returns:
        paths_type:
            A dictionary containing the filepath,
            filename, type (file/dir), extension (if file),
            hidden status, and filesize.
    """

    if not (base_path := pathlib.Path(base_path)).exists():
        raise FileNotFoundError(f"The path '{base_path}' does not exist.")

    path_info = [
        {
            "filepath": str(path.resolve()),
            "filename": path.name,
            "filepath_parent": str(path.parent.resolve()),
            "type": "directory" if path.is_dir() else "file",
            "extension": path.suffix if path.is_file() else None,
            "hidden": path.name.startswith("."),
            "filesize": path.stat().st_size if path.is_file() else None,
        }
        for path in base_path.rglob("*")
        if ignore is None
        or (
            path not in ignore
            and not any(str(path).startswith(ignore_path) for ignore_path in ignore)
            and not any(str(path).endswith(ignore_path) for ignore_path in ignore)
        )
    ]

    return path_info


def find_empty_directories(paths: paths_type) -> paths_type:
    """
    Recursively finds empty directories starting
    from the given base path.

    Args:
        paths (paths_type):
            The base path to start searching
            for empty directories.

    Returns:
        list:
            A list of paths to empty directories.
    """

    directory_children = Counter(path["filepath_parent"] for path in paths)

    return [
        path["filepath"]
        for path in paths
        if path["type"] == "directory" and directory_children[path["filepath"]] == 0
    ]


def count_file_extensions(paths: paths_type) -> Dict[str, int]:
    """
    Counts all file extensions in the given paths
    and returns the count per file extension.

    Args:
        paths (paths_type):
            The paths data structure containing file information.

    Returns:
        Dict[str, int]:
            A dictionary with file extensions
            as keys and their counts as values.
    """
    return Counter(
        path["extension"]
        for path in paths
        if path["type"] == "file" and path["extension"]
    )


def find_similar_directories(
    paths: paths_type, similarity_threshold: float = 0.97
) -> List[tuple]:
    """
    Finds pairs of directory names that
    are extremely similar to each other.

    Args:
        paths (paths_type):
            The paths data structure containing
            file and directory information.
        similarity_threshold (float):
            The threshold above which two
            directory names are considered similar.

    Returns:
        List[tuple]:
            A list of tuples containing pairs of
            similar directory names.
    """

    directories = [path["filepath"] for path in paths if path["type"] == "directory"]
    similar_pairs = []

    for i, dir1 in enumerate(directories):
        for dir2 in directories[i + 1 :]:
            similarity = SequenceMatcher(None, dir1, dir2).ratio()
            if similarity >= similarity_threshold:
                similar_pairs.append((dir1, dir2))

    return similar_pairs


def path_report(
    base_path: str, ignore: Optional[List[str]] = None, print_report: bool = False
) -> Dict[str, Union[Dict[str, int], List[str], List[tuple]]]:
    """
    Generates a report of the local file paths.

    Args:
        base_path (str):
            The base path to analyze.
        ignore (Optional[List[str]]):
            A list of patterns to ignore which is sent to
            the get_path_info function. (e.g.,
            hidden files, specific file types).
        print_report (bool):
            Whether to print the report to the screen.

    Returns:
        dict:
            A dictionary containing the
            path information and empty directories.
    """

    paths = get_path_info(base_path=base_path, ignore=ignore)

    empty_dirs = find_empty_directories(paths=paths)
    similar_dirs = find_similar_directories(paths=paths)

    report = {
        "file_extensions": count_file_extensions(paths=paths),
        "empty_directories": empty_dirs if empty_dirs else [None],
        "similarly_named_directories": similar_dirs if similar_dirs else [None],
    }

    if print_report:
        print("\nnViz Path Report:\n--------------------")
        print("File Extensions:")
        for ext, count in report["file_extensions"].items():
            print(f"  {ext}: {count}")
        print("\nEmpty Directories:")
        for directory in report["empty_directories"]:
            print(f"  {directory}")
        print("\nSimilarly Named Directories:")
        if report["similarly_named_directories"] == [None]:
            print("  None")
        else:
            for dir1, dir2 in report["similarly_named_directories"]:
                print(f"  {dir1} <-> {dir2}")

    return report
