"""
Experiment with GFF image stacks to OME-ZARR with display in Napari.
"""

import pathlib
import shutil
from itertools import groupby
from typing import List

import numpy as np
import tifffile as tiff

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
output_path = f"{relpath}/data/example_output.ome.tiff"

# Clean up any previous output
shutil.rmtree(output_path, ignore_errors=True)


# Function to write OME-TIFF
def write_ome_tiff(
    output_path: str,
    data: np.ndarray,
    axes: str,
    resolution: List[float],
    channel_names: List[str],
) -> None:
    """
    Write data to an OME-TIFF file with specified metadata.

    Args:
        output_path (str):
            The path where the OME-TIFF file will be saved.
        data (np.ndarray):
            The image data to be written to the OME-TIFF file.
        axes (str):
            The axes of the image data (e.g., 'ZYX', 'CZYX').
        resolution (List[float]):
            The physical size of each pixel in micrometers (µm) for each axis.
            The order should be [Z, Y, X].
        channel_names (List[str]):
            The names of the channels in the image data.

    Returns:
        None
    """

    with tiff.TiffWriter(output_path, bigtiff=True) as tif:
        options = {
            "photometric": "minisblack",
            "metadata": {
                "axes": axes,
                "PhysicalSizeX": resolution[2],  # X resolution
                "PhysicalSizeY": resolution[1],  # Y resolution
                "PhysicalSizeZ": resolution[0],  # Z resolution
                "PhysicalSizeXUnit": "µm",
                "PhysicalSizeYUnit": "µm",
                "PhysicalSizeZUnit": "µm",
                "Channel": [{"Name": name} for name in channel_names],
            },
        }

        tif.write(data, **options)


# Prepare the data for writing
images_data = []
labels_data = []
channel_names = []
label_names = []

# Collect image data
for channel, stack in frame_zstacks["images"].items():
    images_data.append(stack)
    channel_names.append(channel)

# Collect label data
for compartment_name, stack in frame_zstacks["labels"].items():
    labels_data.append(stack)
    # note: we add the labels distinction to help
    # differentiate between channels and labels
    label_names.append(f"{compartment_name} (labels)")

# Stack the images and labels along a new axis for channels
images_data = np.stack(images_data, axis=0)
labels_data = np.stack(labels_data, axis=0)

# Combine images and labels into a single array
combined_data = np.concatenate((images_data, labels_data), axis=0)

# Combine channel names and label names into a single list
combined_channel_names = channel_names + label_names

# Write the combined data to a single OME-TIFF
write_ome_tiff(
    output_path,
    combined_data,
    "CZYX",
    [scaling_values[0], scaling_values[1], scaling_values[2]],
    combined_channel_names,
)

print(f"OME-TIFF written to {output_path}")


# Verify that the file is an OME-TIFF
def verify_ome_tiff(file_path: str) -> None:
    """Verify that the file is an OME-TIFF.

    Args:
        file_path (str):
            The path to the file to be verified.

    Raises:
        ValueError:
            If the file is not an OME-TIFF.
    """
    try:
        with tiff.TiffFile(file_path) as tif:
            is_ome = tif.is_ome
            print(f"{file_path} is OME-TIFF: {is_ome}")
            if not is_ome:
                raise ValueError(f"{file_path} is not an OME-TIFF file.")
    except Exception as e:
        raise ValueError(f"Error verifying OME-TIFF file: {e}")


verify_ome_tiff(output_path)
