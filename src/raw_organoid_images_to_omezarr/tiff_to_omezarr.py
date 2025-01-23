"""
Experiment with GFF image stacks to OME-ZARR with display in Napari.
"""

import pathlib
import shutil
from itertools import groupby

import numpy as np
import tifffile as tiff
import zarr
from ome_zarr.io import parse_url
from ome_zarr.writer import write_image

from gff3d_utils.view import (
    extract_z_slice_number_from_filename,
    gather_scaling_info_from_scaninfoxml,
)

# create a filename code to channel name mapping
# (filename codes are found within the filenames provided)
filename_code_channel_map = {
    "405": "Hoechst 33342",
    "488": "Concanavalin A",
    "555": "WGA+ Phalloidin",
    "640": "Mitotracker Deep Red",
    "TRANS": "Bright Field",
}

relpath = pathlib.Path(__file__).parent

# Set paths used below
image_directory = pathlib.Path(
    f"{relpath}/data/GFF-data/originals/NF0014-Thawed 3 (Raw image files)-Combined"
    "/C10-1/C10-1"
)
scaninfo_file = pathlib.Path(
    f"{relpath}/data/GFF-data/originals/NF0014-Thawed 3 (Raw image files)-Combined"
    "/C10-1/ScanInfo.xml"
)
mask_directory = pathlib.Path(f"{relpath}/data/GFF-data/masks/C10-1")

# gather scaling details
scaling_values = gather_scaling_info_from_scaninfoxml(scaninfo_file)

# build a reference to the observations
frame_files = {
    # gather data from original images
    "images": {
        # images include a channel code which is mentioned
        # above in the filename_code_channel_map
        filename_code_channel_map[filename_code]: sorted(
            files, key=lambda x: extract_z_slice_number_from_filename(x.name)
        )
        for filename_code, files in groupby(
            sorted(
                [
                    file
                    for file in image_directory.glob("*.tif")
                    # ignore the files with "Merge" in the name
                    if file.name.split("_")[1] != "Merge"
                ],
                key=lambda x: x.name.split("_")[1],
            ),
            key=lambda x: x.name.split("_")[1],
        )
    },
    "labels": {
        # the masks include a compartment name which is mentioned
        # in the mask_channel_map
        label_name: next(iter(file))
        for label_name, file in groupby(
            sorted(
                mask_directory.glob("*.tiff"),
                key=lambda x: x.name.split("_")[0],
            ),
            key=lambda x: x.name.split("_")[0],
        )
    },
}

# Debug: show channel keys and file counts
print(frame_files["images"].keys())
for channel, files in frame_files["images"].items():
    print(f"Channel: {channel}, Files: {len(files)}")
    for file in files:
        print(f"  {file.name}")

# Debug: show channel keys and file counts
print(frame_files["images"].keys())
for channel, files in frame_files["images"].items():
    print(f"Channel: {channel}, Files: {len(files)}")

# Load images into memory via stacks
frame_zstacks = {
    "images": {
        channel: np.stack([tiff.imread(file) for file in files], axis=0).astype(
            np.uint16
        )
        for channel, files in frame_files["images"].items()
    },
    "labels": {
        channel: tiff.imread(tiff_file).astype(np.uint16)
        for channel, tiff_file in frame_files["labels"].items()
    },
}

# Debug: show stack shapes
for channel, stack in frame_zstacks["images"].items():
    print(f"Channel: {channel}, Stack shape: {stack.shape}")

# Define the output path
output_path = f"{relpath}/data/example_output.zarr"

# Clean up any previous output
shutil.rmtree(output_path, ignore_errors=True)

# Parse URL and ensure store is compatible
store = parse_url(output_path, mode="w").store
# Ensure we are working with a Zarr group
root = zarr.group(store, overwrite=True)

# Write each channel separately to the Zarr file with no compression
# Save images to OME-Zarr format
images_group = root.create_group("images")
for channel, stack in frame_zstacks["images"].items():
    write_image(
        image=stack,
        group=(group := images_group.create_group(channel)),
        axes="zyx",  # Specify the axes order for each channel
        dtype="uint16",  # Ensure the dtype is set correctly
        scaler=None,  # Disable scaler
    )
    # Set the units attribute for the group to "micrometers"
    group.attrs["units"] = "micrometers"

    # Define the multiscales metadata for the group
    group.attrs["multiscales"] = [
        {
            "datasets": [
                {
                    "path": "0",  # Path to the dataset
                    "coordinateTransformations": [
                        {
                            "type": "scale",
                            "scale": list(scaling_values),
                        }  # Apply scaling values
                    ],
                }
            ],
            "axes": [
                {
                    "name": "z",
                    "unit": "micrometer",
                    "type": "space",
                },  # Define the z-axis
                {
                    "name": "y",
                    "unit": "micrometer",
                    "type": "space",
                },  # Define the y-axis
                {
                    "name": "x",
                    "unit": "micrometer",
                    "type": "space",
                },  # Define the x-axis
            ],
        }
    ]

# Save masks to OME-Zarr format
labels_group = root.create_group("labels")
for compartment_name, stack in frame_zstacks["labels"].items():
    write_image(
        image=stack,
        group=(group := labels_group.create_group(compartment_name)),
        axes="zyx",  # Specify the axes order for each mask
        dtype="uint16",  # Ensure the dtype is set correctly
        scaler=None,  # Disable scaler
    )
    # Set the units attribute for the group to "micrometers"
    group.attrs["units"] = "micrometers"

    # Define the multiscales metadata for the group
    group.attrs["multiscales"] = [
        {
            "datasets": [
                {
                    "path": "0",  # Path to the dataset
                    "coordinateTransformations": [
                        {
                            "type": "scale",
                            "scale": list(scaling_values),
                        }  # Apply scaling values
                    ],
                }
            ],
            "axes": [
                {
                    "name": "z",
                    "unit": "micrometer",
                    "type": "space",
                },  # Define the z-axis
                {
                    "name": "y",
                    "unit": "micrometer",
                    "type": "space",
                },  # Define the y-axis
                {
                    "name": "x",
                    "unit": "micrometer",
                    "type": "space",
                },  # Define the x-axis
            ],
        }
    ]

print(f"OME-Zarr written to {output_path}")

# Debug: show shape of input
print(f"Shape of input: {np.array(frame_zstacks['images'].values()).shape}")

# Check Zarr file structure
frame_zarr = zarr.open(output_path, mode="r")
print(frame_zarr.tree())
