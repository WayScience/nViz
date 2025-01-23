"""
Viewing data from a Zarr store in Neuroglancer
"""

import pathlib
import time
import webbrowser

import neuroglancer
from cloudvolume import CloudVolume

# Set up Neuroglancer
neuroglancer.set_server_bind_address("localhost")

relpath = pathlib.Path(__file__).parent

# Define the path to the Zarr store
zarr_path = f"{relpath}/data/example_output.zarr"

# Create a CloudVolume instance
vol = CloudVolume(
    f"file://{zarr_path}/images/Concanavalin A", mip=0, bounded=True, fill_missing=True
)

# Ensure the volume is correctly set up
vol.info["scales"][0]["resolution"] = [
    0.1006,
    0.1006,
    1,
]  # Example resolution in micrometers
vol.info["scales"][0]["voxel_offset"] = [
    0,
    0,
    0,
    0,
]  # Adjusted to match the rank of the data
vol.info["scales"][0]["size"] = vol.shape
vol.info["type"] = "uint16"
vol.info["data_type"] = "uint16"
vol.commit_info()

# Check the shape of the data
data_shape = vol.shape
print(f"Data shape: {data_shape}")

# Adjust the coordinate space to match the data dimensions
coordinate_space = neuroglancer.CoordinateSpace(
    names=["c", "z", "y", "x"], units="mm", scales=[1, 0.1006, 0.1006, 0.1006]
)

# Open the volume in Neuroglancer
viewer = neuroglancer.Viewer()
with viewer.txn() as s:
    s.layers.append(
        name="Concanavalin A",
        layer=neuroglancer.LocalVolume(
            data=vol, dimensions=coordinate_space, voxel_offset=(0, 0, 0, 0)
        ),
    )

# Print the Neuroglancer viewer URL
print(f"Neuroglancer viewer URL: {viewer.get_viewer_url()}")
webbrowser.open_new_tab(viewer.get_viewer_url())

time.sleep(500)
