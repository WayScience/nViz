"""
Experiment with randomized image zstacks to OME-ZARR with display in Napari.
"""

import pathlib
import shutil

import napari
import numpy as np
import zarr
from ome_zarr.io import parse_url
from ome_zarr.writer import write_image

channels = [
    "Channel A",
    "Channel B",
    "Channel C",
    "Channel D",
    "Channel E",
]

relpath = pathlib.Path(__file__).parent

# Set common static scaling values
scaling_values = (1.0, 0.1, 0.1)  # (z, y, x) in microns

# Generate random data for z-slices
num_z_slices = 45
image_shape = (1537, 1540)  # Example shape, adjust as needed

channels = {
    channel: [
        np.random.randint(0, 65535, size=image_shape, dtype=np.uint16)
        for _ in range(num_z_slices)
    ]
    for channel in channels
}

# Debug: show channel keys and file counts
print(channels.keys())
for channel, files in channels.items():
    print(f"Channel: {channel}, Slices: {len(files)}")

# Load images into memory via stacks
zstacks = {
    channel: np.stack(files, axis=0).astype(np.uint16)
    for channel, files in channels.items()
}

# Debug: show stack shapes
for channel, stack in zstacks.items():
    print(f"Channel: {channel}, Stack shape: {stack.shape}")

# Define the output path
output_path = f"{relpath}/data/randomized_example_output.zarr"

# Clean up any previous output
shutil.rmtree(output_path, ignore_errors=True)

# Parse URL and ensure store is compatible
store = parse_url(output_path, mode="w").store
group = zarr.group(store, overwrite=True)  # Ensure we are working with a Zarr group

# Write each channel separately to the Zarr file with no compression
for channel, stack in zstacks.items():
    write_image(
        stack,
        group.create_group(channel),
        axes="zyx",  # Specify the axes order for each channel
        dtype="uint16",
        scaler=None,  # Disable scaler
    )

print(f"OME-Zarr written to {output_path}")

# Debug: show shape of input
print(f"Shape of input: {np.array(list(zstacks.values())).shape}")

# Check Zarr file structure
z = zarr.open(output_path, mode="r")
print(z.tree())

# Visualize with napari, start in 3d mode
viewer = napari.Viewer(ndisplay=3)

# Iterate through each channel in the Zarr file
for channel_name in sorted(z.keys(), reverse=True):
    print(f"Opening {channel_name} in Napari...")
    viewer.add_image(z[channel_name]["0"][:], name=channel_name, scale=scaling_values)

# Start the Napari event loop
napari.run()
