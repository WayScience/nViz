"""
Utilities for testing.
"""

import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Tuple

import pytest
import synapseclient
import synapseutils

# set a pytest marker to skip tests if the environment variable
# for SYNAPSE_AUTH_TOKEN is not set. This is used to skip
# tests that require access to Synapse data.
skip_if_no_synapse_token = pytest.mark.skipif(
    os.environ.get("SYNAPSE_AUTH_TOKEN") is None,
    reason="Set SYNAPSE_AUTH_TOKEN to run Sage Bionetworks Synapse tests.",
)

# data examples for use with pytest parameterized tests
# (creating a data value here because it's simpler to use
# than a fixture inside parameterized tests).
example_data_for_image_tests = [
    # test example data without labels
    (
        "tests/data/random_tiff_z_stacks/Z99",
        None,
        "output.zarr",
        {
            "111": "Channel A",
            "222": "Channel B",
            "333": "Channel C",
            "444": "Channel D",
            "555": "Channel E",
        },
        (1.0, 0.1, 0.1),
        None,
        None,
    ),
    # test example data with labels
    (
        "tests/data/random_tiff_z_stacks/Z99",
        "tests/data/random_tiff_z_stacks/labels",
        "output.zarr",
        {
            "111": "Channel A",
            "222": "Channel B",
            "333": "Channel C",
            "444": "Channel D",
            "555": "Channel E",
        },
        (1.0, 0.1, 0.1),
        None,
        ["compartment (labels)"],
    ),
    # test example data with labels and ignore a channel
    (
        "tests/data/random_tiff_z_stacks/Z99",
        "tests/data/random_tiff_z_stacks/labels",
        "output.zarr",
        {
            "111": "Channel A",
            "222": "Channel B",
            "333": "Channel C",
            "444": "Channel D",
            "555": "Channel E",
        },
        (1.0, 0.1, 0.1),
        ["555"],
        ["compartment (labels)"],
    ),
]

# real data for use with pytest parameterized tests
# (creating a data value here because it's simpler to use
# than a fixture inside parameterized tests).
real_data_for_image_tests = [
    # test example data without labels
    (
        "tests/data/synapse/download/C10-1/C10-1",
        None,
        "output.zarr",
        {
            "405": "Hoechst 33342",
            "488": "Concanavalin A",
            "555": "WGA+ Phalloidin",
            "640": "Mitotracker Deep Red",
            "TRANS": "Bright Field",
        },
        (1.0, 0.1, 0.1),
        ["Merge"],
        None,
    ),
]


def download_file(
    syn: synapseclient.Synapse, file_id: str, target_dir: Path, file_name: str
) -> None:
    """
    Download a single file from Synapse if it doesn't already exist.

    Args:
        syn (synapseclient.Synapse):
            The Synapse client instance.
        file_id (str):
            The Synapse ID of the file to download.
        target_dir (Path):
            The local directory where the file will be saved.
        file_name (str):
            The name of the file to save locally.

    Returns:
        None
    """
    target_file = target_dir / file_name
    # note: we add coverage pragma below to avoid discrepancies
    # with coverage generation between various systems and
    # specialized CI configuration.
    if target_file.exists():
        print(f"File already exists, skipping: {target_file}")  # pragma: no cover
        return  # pragma: no cover
    file_entity = syn.get(file_id, downloadLocation=target_dir)
    print(f"Downloaded: {file_entity.path}")  # pragma: no cover


def download_synapse_folder(
    syn: synapseclient.Synapse, folder_id: str, local_dir: Path, max_workers: int = 8
) -> None:
    """
    Recursively download all files from a Synapse folder,
    preserving the folder structure.

    Args:
        syn (synapseclient.Synapse):
            The Synapse client instance.
        folder_id (str):
            The Synapse ID of the folder to download.
        local_dir (Path):
            The local directory where the folder
            structure and files will be saved.
        max_workers (int):
            The maximum number of threads to use
            for parallel downloads. Defaults to 8.

    Returns:
        None
    """
    local_dir.mkdir(parents=True, exist_ok=True)

    for dirpath, subdirs, files in synapseutils.walk(syn, folder_id):
        # Construct the relative path for the current folder
        relative_path = Path(dirpath[0].replace(folder_id, "").strip("/"))
        target_dir = local_dir / relative_path
        target_dir.mkdir(
            parents=True, exist_ok=True
        )  # Create the directory if it doesn't exist

        # Use ThreadPoolExecutor to parallelize file downloads
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for file_name, file_id in files:
                executor.submit(download_file, syn, file_id, target_dir, file_name)


def run_cli_command(command: str) -> Tuple[str, str, int]:
    """
    Run a CLI command using subprocess and capture the output and return code.

    Args:
        command (list): The command to run as a list of strings.

    Returns:
        tuple: (str: stdout, str: stderr, int: returncode)
    """

    result = subprocess.run(args=command, capture_output=True, text=True, check=False)
    return result.stdout, result.stderr, result.returncode
