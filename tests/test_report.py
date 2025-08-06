"""
Tests for the report module
"""

import pathlib
from typing import Dict, Union

import pytest

from nviz.report import (
    count_file_extensions,
    find_empty_directories,
    find_similar_directories,
    get_path_info,
    path_report,
)

paths_type = Dict[str, Union[str, bool, int, float, None]]


@pytest.mark.parametrize(
    "base_path", ["tests/does_not_exist", "tests/data/file_and_folder_issues"]
)
def test_get_path_info(base_path: str):
    """
    Test the get_path_info function.
    """
    try:
        path_info = get_path_info(base_path)
        assert isinstance(path_info, list)
        for item in path_info:
            assert "filepath" in item
            assert "filename" in item
            assert "type" in item
            assert "hidden" in item
            if item["type"] == "file":
                assert "extension" in item
                assert "filesize" in item
    except FileNotFoundError:
        pass  # Handle non-existent paths gracefully


@pytest.mark.parametrize("paths", ["tests/data/file_and_folder_issues"])
def test_find_empty_directories(paths: paths_type):
    """
    Test the find_empty_directories function.
    """

    empty_dirs = find_empty_directories(
        paths=get_path_info(base_path=paths, ignore=[".gitkeep"])
    )
    assert isinstance(empty_dirs, list)
    for dir_path in empty_dirs:
        assert pathlib.Path(dir_path).is_dir()
        assert not any(
            path
            for path in pathlib.Path(dir_path).iterdir()
            if not str(path).endswith(".gitkeep")
        )


@pytest.mark.parametrize("paths", ["tests/data/file_and_folder_issues"])
def test_count_file_extensions(paths: paths_type):
    """
    Test the count_file_extensions function.
    """
    extension_counts = count_file_extensions(paths=get_path_info(base_path=paths))
    assert isinstance(extension_counts, dict)
    for ext, count in extension_counts.items():
        assert isinstance(ext, str)
        assert isinstance(count, int)


@pytest.mark.parametrize(
    "paths, similarity_threshold", [("tests/data/file_and_folder_issues", 0.97)]
)
def test_find_similar_directories(paths: paths_type, similarity_threshold: float):
    """
    Test the find_similar_directories function.
    """
    similar_dirs = find_similar_directories(
        paths=get_path_info(base_path=paths), similarity_threshold=similarity_threshold
    )
    assert isinstance(similar_dirs, list)
    for dir1, dir2 in similar_dirs:
        assert isinstance(dir1, str)
        assert isinstance(dir2, str)
        assert dir1 != dir2


@pytest.mark.parametrize(
    "base_path", ["tests/bogus/directory", "tests/data/file_and_folder_issues"]
)
def test_path_report(base_path: str):
    """
    Test the path_report function.
    """

    try:
        report = path_report(
            base_path=base_path, ignore=[".gitkeep"], print_report=True
        )
        assert isinstance(report, dict)
        assert "file_extensions" in report
        assert "empty_directories" in report
        assert "similarly_named_directories" in report
    except FileNotFoundError:
        pass  # Handle non-existent paths gracefully
