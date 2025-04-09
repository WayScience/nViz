"""
conftest.py for pytest fixtures and related
"""

import os
import pytest
import synapseclient
import pathlib
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
    # Synapse folder ID and local directory
    folder_id = "syn65987279"  # Replace with the actual Synapse folder ID
    local_dir = pathlib.Path("tests/data/synapse/download/C10-1")

    # Check if the directory already exists and contains files
    if not local_dir.exists() or not any(local_dir.iterdir()):
        print(f"Downloading Synapse data to {local_dir}...")

        # Initialize Synapse client and log in
        syn = synapseclient.Synapse()
        syn.login(authToken=os.environ["SYNAPSE_AUTH_TOKEN"])  # Requires valid token

        # Download the Synapse folder
        download_synapse_folder(
            syn=syn, folder_id=folder_id, local_dir=pathlib.Path(local_dir).parent
        )

    else:
        print(f"Synapse data already exists at {local_dir}, skipping download.")

    return local_dir
