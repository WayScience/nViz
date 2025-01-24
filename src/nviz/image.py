"""
Experiment with GFF image stacks to OME-ZARR with display in Napari.
"""

import pathlib
import shutil
from itertools import groupby
from typing import Union, Tuple, List, Optional, Dict
import os
import numpy as np
import tifffile as tiff
import zarr
from ome_zarr.io import parse_url as zarr_parse_url
from ome_zarr.writer import write_image as zarr_write_image

from .meta import (
    extract_z_slice_number_from_filename,
    generate_ome_xml
)


def tiff_to_zarr(
    image_dir: str,
    label_dir: Optional[str],
    output_path: str,
    channel_map: Dict[str, str],
    scaling_values: Union[List[int], Tuple[int]],
    overwrite: bool = False,
    debug: bool = False,
) -> str:
    """
    Convert TIFF files to OME-Zarr format.

    Args:
        image_dir (str):
            Directory containing TIFF image files.
        label_dir (Optional[str]):
            Directory containing label TIFF files.
        output_path (str):
            Path to save the output OME-Zarr file.
        channel_map (Dict[str, str]):
            Mapping from filename codes to channel names.
        scaling_values (Union[List[int], Tuple[int]]):
            Scaling values for the images.
        overwrite (bool):
            Whether to overwrite existing output. Default is False.
        debug (bool):
            Whether to print debug information. Default is False.

    Returns:
        str: Path to the output OME-Zarr file.
    """

    if not pathlib.Path(image_dir).is_dir():
        raise NotADirectoryError(f"Image directory {image_dir} does not exist.")

    # build a reference to the observations
    frame_files = {
        "images": {
            channel_map[filename_code]: sorted(
                files, key=lambda x: extract_z_slice_number_from_filename(x.name)
            )
            for filename_code, files in groupby(
                sorted(
                    [
                        file
                        for file in os.scandir(image_dir)
                        if (file.name.endswith(".tif") or file.name.endswith(".tiff"))
                        and file.name.split("_")[1] != "Merge"
                    ],
                    key=lambda x: x.name.split("_")[1],
                ),
                key=lambda x: x.name.split("_")[1],
            )
        }
    }

    if label_dir is not None:
        frame_files["labels"] = {
            f"{pathlib.Path(label_name).stem} (labels)": next(iter(file))
            for label_name, file in groupby(
                sorted(
                    os.scandir(label_dir),
                    key=lambda x: x.name.split("_")[0],
                ),
                key=lambda x: x.name.split("_")[0],
            )
        }

    # Debug: show channel keys and file counts
    if debug:
        print(frame_files["images"].keys())
        for channel, files in frame_files["images"].items():
            print(f"Channel: {channel}, Files: {len(files)}")
            for file in files:
                print(f"  {file.name}")

    # Load images into memory via stacks
    frame_zstacks = {
        "images": {
            channel: np.stack(
                [tiff.imread(file.path) for file in files], axis=0
            ).astype(np.uint16)
            for channel, files in frame_files["images"].items()
        }
    }

    if label_dir:
        frame_zstacks["labels"] = {
            channel: tiff.imread(tiff_file.path).astype(np.uint16)
            for channel, tiff_file in frame_files["labels"].items()
        }

    # Debug: show stack shapes
    if debug:
        for channel, stack in frame_zstacks["images"].items():
            print(f"Channel: {channel}, Stack shape: {stack.shape}")

    # Clean up any previous output
    if overwrite and pathlib.Path(output_path).is_dir():
        shutil.rmtree(output_path, ignore_errors=True)
    elif pathlib.Path(output_path).is_dir():
        raise FileExistsError(
            f"Output path {output_path} already exists. Use overwrite=True to overwrite."
        )

    # Parse URL and ensure store is compatible
    store = zarr_parse_url(output_path, mode="w").store
    # Ensure we are working with a Zarr group
    root = zarr.group(store, overwrite=True)

    # create scaling metadata
    scale_metadata = [
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

    # Write each channel separately to the Zarr file with no compression
    # Save images to OME-Zarr format
    images_group = root.create_group("images")
    for channel, stack in frame_zstacks["images"].items():
        zarr_write_image(
            image=stack,
            group=(group := images_group.create_group(channel)),
            axes="zyx",  # Specify the axes order for each channel
            dtype="uint16",  # Ensure the dtype is set correctly
            scaler=None,  # Disable scaler
        )
        # Set the units attribute for the group to "micrometers"
        group.attrs["units"] = "micrometers"

        # Define the multiscales metadata for the group
        group.attrs["multiscales"] = scale_metadata

    if label_dir:
        # Save masks to OME-Zarr format
        labels_group = root.create_group("labels")
        for compartment_name, stack in frame_zstacks["labels"].items():
            zarr_write_image(
                image=stack,
                group=(group := labels_group.create_group(compartment_name)),
                axes="zyx",  # Specify the axes order for each mask
                dtype="uint16",  # Ensure the dtype is set correctly
                scaler=None,  # Disable scaler
            )
            # Set the units attribute for the group to "micrometers"
            group.attrs["units"] = "micrometers"

            # Define the multiscales metadata for the group
            group.attrs["multiscales"] = scale_metadata

    print(f"OME-Zarr written to {output_path}")

    # Debug: show shape of input
    if debug:
        print(
            f"Shape of input: {np.array(list(frame_zstacks['images'].values())).shape}"
        )

    # Check Zarr file structure
    frame_zarr = zarr.open(output_path, mode="r")
    if debug:
        print(frame_zarr.tree())

    return output_path




def tiff_to_ometiff(
    image_dir: str,
    label_dir: Optional[str],
    output_path: str,
    channel_map: Dict[str, str],
    scaling_values: Union[List[int], Tuple[int]],
    overwrite: bool = False,
    debug: bool = False,
) -> str:
    """
    Convert TIFF files to OME-TIFF format.

    Args:
        image_dir (str):
            Directory containing TIFF image files.
        label_dir (Optional[str]):
            Directory containing label TIFF files.
        output_path (str):
            Path to save the output OME-TIFF file.
        channel_map (Dict[str, str]):
            Mapping from filename codes to channel names.
        scaling_values (Union[List[int], Tuple[int]]):
            Scaling values for the images.
        overwrite (bool):
            Whether to overwrite existing output. Default is False.
        debug (bool):
            Whether to print debug information. Default is False.

    Returns:
        str: Path to the output OME-TIFF file.
    """

    if not pathlib.Path(image_dir).is_dir():
        raise NotADirectoryError(f"Image directory {image_dir} does not exist.")

    # build a reference to the observations
    frame_files = {
        "images": {
            channel_map.get(filename_code, f"Unknown_{filename_code}"): sorted(
                files, key=lambda x: extract_z_slice_number_from_filename(x.name)
            )
            for filename_code, files in groupby(
                sorted(
                    [
                        file
                        for file in os.scandir(image_dir)
                        if (file.name.endswith(".tif") or file.name.endswith(".tiff"))
                        and file.name.split("_")[1] != "Merge"
                    ],
                    key=lambda x: x.name.split("_")[1],
                ),
                key=lambda x: x.name.split("_")[1],
            )
        }
    }

    if label_dir:
        frame_files["labels"] = {
            label_name: next(iter(file))
            for label_name, file in groupby(
                sorted(
                    pathlib.Path(label_dir).glob("*.tiff"),
                    key=lambda x: x.name.split("_")[0],
                ),
                key=lambda x: x.name.split("_")[0],
            )
        }

    # Debug: show channel keys and file counts
    if debug:
        print("Frame files (images):")
        for channel, files in frame_files["images"].items():
            print(f"Channel: {channel}, Files: {[file.name for file in files]}")

        if "labels" in frame_files:
            print("Frame files (labels):")
            for label, file in frame_files["labels"].items():
                print(f"Label: {label}, File: {file.name}")

    # Load images into memory via stacks
    frame_zstacks = {
        "images": {
            channel: np.stack(
                [tiff.imread(file.path) for file in files], axis=0
            ).astype(np.uint16)
            for channel, files in frame_files["images"].items()
        }
    }

    if label_dir:
        frame_zstacks["labels"] = {
            channel: tiff.imread(tiff_file.path).astype(np.uint16)
            for channel, tiff_file in frame_files["labels"].items()
        }

    # Debug: show stack shapes
    if debug:
        for channel, stack in frame_zstacks["images"].items():
            print(f"Channel: {channel}, Stack shape: {stack.shape}")

        if "labels" in frame_zstacks:
            for label, stack in frame_zstacks["labels"].items():
                print(f"Label: {label}, Stack shape: {stack.shape}")

    if overwrite:
        # Clean up any previous output
        shutil.rmtree(output_path, ignore_errors=True)

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
    if label_dir:
        for compartment_name, stack in frame_zstacks["labels"].items():
            labels_data.append(stack)
            label_names.append(f"{compartment_name} (labels)")

    # Stack the images and labels along a new axis for channels
    images_data = np.stack(images_data, axis=0)
    if labels_data:
        labels_data = np.stack(labels_data, axis=0)
        combined_data = np.concatenate((images_data, labels_data), axis=0)
        combined_channel_names = channel_names + label_names
    else:
        combined_data = images_data
        combined_channel_names = channel_names

    # Generate OME-XML metadata
    ome_metadata = {
        "SizeC": combined_data.shape[0],
        "SizeZ": combined_data.shape[1],
        "SizeY": combined_data.shape[2],
        "SizeX": combined_data.shape[3],
        "PhysicalSizeX": scaling_values[2],
        "PhysicalSizeY": scaling_values[1],
        "PhysicalSizeZ": scaling_values[0],
        # note: we use 7-bit ascii compatible characters below
        "PhysicalSizeXUnit": "um",
        "PhysicalSizeYUnit": "um",
        "PhysicalSizeZUnit": "um",
        "Channel": [{"Name": name} for name in combined_channel_names],
    }
    ome_xml = generate_ome_xml(ome_metadata)

    # Write the combined data to a single OME-TIFF
    with tiff.TiffWriter(output_path, bigtiff=True) as tif:
        tif.write(combined_data, description=ome_xml, photometric='minisblack')

    if debug:
        print(f"OME-TIFF written to {output_path}")

    return output_path
