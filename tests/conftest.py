"""
conftest.py for pytest fixtures and related
"""

import os
import pathlib

import pytest
import synapseclient

from tests.utils import download_synapse_folder


@pytest.fixture(scope="session")
def ensure_synapse_data():
    """
    Pytest fixture to ensure that the required Synapse data exists locally.
    Downloads the Synapse folder if the files are not already present.

    Returns:
        pathlib.Path:
            The local directory where the Synapse data is stored.
    """

    # check that we have a
    assert os.environ.get("SYNAPSE_AUTH_TOKEN"), (
        "SYNAPSE_AUTH_TOKEN is not set in the environment"
    )

    # Synapse folder ID and local directory
    folder_id = "syn65987279"
    local_dir = pathlib.Path("tests/data/synapse/download/C10-1")

    # Check if the directory already exists and contains files
    if not local_dir.exists() or not any(local_dir.iterdir()):
        print(f"Downloading Synapse data to {local_dir}...")

        # Initialize Synapse client and log in
        syn = synapseclient.Synapse()
        syn.login(
            authToken=os.environ.get("SYNAPSE_AUTH_TOKEN")
        )  # Requires valid token

        # Download the Synapse folder
        download_synapse_folder(
            syn=syn, folder_id=folder_id, local_dir=pathlib.Path(local_dir).parent
        )

    else:
        print(f"Synapse data already exists at {local_dir}, skipping download.")

    # Verify files exist
    assert local_dir.exists(), f"Directory {local_dir} does not exist"
    assert any(local_dir.iterdir()), f"No files found in {local_dir}"

    return local_dir
