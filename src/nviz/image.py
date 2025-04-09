"""
Experiment with GFF image stacks to OME-ZARR with display in Napari.
"""

import os
import pathlib
from itertools import groupby
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import tifffile as tiff
import zarr
from ome_zarr.io import parse_url as zarr_parse_url
from ome_zarr.writer import write_image as zarr_write_image

from .image_meta import extract_z_slice_number_from_filename, generate_ome_xml


def image_set_to_arrays(
    image_dir: str,
    channel_map: Dict[str, str],
    label_dir: Optional[str] = None,
    ignore: Optional[List[str]] = ["Merge"],
) -> Dict[str, Dict[str, np.ndarray]]:
    """
    Read a set of images as an array of images.
    We follow a convention of splitting the following
    into separate nested dictionaries for use by
    other functions within this project.

    - "images": original images
    - "labels": images which represent objects of interest
        within the original "images"

    Args:
        image_dir (str):
            Directory containing TIFF image files.
        channel_map (Dict[str, str]):
            Mapping from filename codes to channel names.
        label_dir (Optional[str]):
            Directory containing label TIFF files. Defaults to None.
        ignore (Optional[List[str]]):
            List of filename codes to ignore.
            Defaults to ["Merge"], which is a
            code for merged images.

    Returns:
        Dict[str, Dict[str, np.ndarray]]:
            A dictionary containing two keys: "images" and "labels".
            Each key maps to another dictionary where the keys are
            channel names and the values are numpy arrays of images.
    """
    # build a reference to the observations
    zstack_arrays = {
        "images": {
            channel_map.get(filename_code, filename_code): np.stack(
                [
                    tiff.imread(tiff_file.path).astype(np.uint16)
                    for tiff_file in sorted(
                        files,
                        key=lambda x: extract_z_slice_number_from_filename(x.name),
                    )
                ]
            ).astype(np.uint16)
            for filename_code, files in groupby(
                sorted(
                    [
                        file
                        for file in os.scandir(image_dir)
                        if (file.name.endswith(".tif") or file.name.endswith(".tiff"))
                        and (
                            file.name.split("_")[1] not in ignore
                            if ignore is not None
                            else True
                        )
                    ],
                    key=lambda x: x.name.split("_")[1],
                ),
                key=lambda x: x.name.split("_")[1],
            )
        }
    }

    if label_dir:
        zstack_arrays["labels"] = {
            f"{pathlib.Path(label_name).stem} (labels)": tiff.imread(
                next(iter(file)).path
            ).astype(np.uint16)
            for label_name, file in groupby(
                sorted(
                    [
                        file
                        for file in os.scandir(label_dir)
                        if (file.name.endswith(".tif") or file.name.endswith(".tiff"))
                        and (
                            file.name.split("_")[0] not in ignore
                            if ignore is not None
                            else True
                        )
                    ],
                    key=lambda x: x.name.split("_")[0],
                ),
                key=lambda x: x.name.split("_")[0],
            )
        }

    return zstack_arrays


def tiff_to_zarr(  # noqa: PLR0913
    image_dir: str,
    output_path: str,
    channel_map: Dict[str, str],
    scaling_values: Union[List[int], Tuple[int]],
    label_dir: Optional[str] = None,
    ignore: Optional[List[str]] = ["Merge"],
) -> str:
    """
    Convert TIFF files to OME-Zarr format.

    Args:
        image_dir (str):
            Directory containing TIFF image files.
        output_path (str):
            Path to save the output OME-Zarr file.
        channel_map (Dict[str, str]):
            Mapping from filename codes to channel names.
        scaling_values (Union[List[int], Tuple[int]]):
            Scaling values for the images.
        label_dir (Optional[str]):
            Directory containing label TIFF files. Defaults to None.
        ignore (Optional[List[str]]):
            List of filename codes to ignore.
            Defaults to ["Merge"], which is a
            code for merged images.

    Returns:
        str: Path to the output OME-Zarr file.
    """

    # except on dir already existing
    if pathlib.Path(output_path).is_dir():
        raise FileExistsError(
            (
                f"Output path {output_path} already exists."
                "Please remove before creating a new Zarr."
            )
        )

    if not pathlib.Path(image_dir).is_dir():
        raise NotADirectoryError(f"Image directory {image_dir} does not exist.")

    # build a reference to the observations
    frame_zstacks = image_set_to_arrays(
        image_dir=image_dir, label_dir=label_dir, channel_map=channel_map, ignore=ignore
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

    return output_path


def tiff_to_ometiff(  # noqa: PLR0913
    image_dir: str,
    output_path: str,
    channel_map: Dict[str, str],
    scaling_values: Union[List[int], Tuple[int]],
    label_dir: Optional[str] = None,
    ignore: Optional[List[str]] = ["Merge"],
) -> str:
    """
    Convert TIFF files to OME-TIFF format.

    Args:
        image_dir (str):
            Directory containing TIFF image files.
        output_path (str):
            Path to save the output OME-TIFF file.
        channel_map (Dict[str, str]):
            Mapping from filename codes to channel names.
        scaling_values (Union[List[int], Tuple[int]]):
            Scaling values for the images.
        label_dir (Optional[str]):
            Directory containing label TIFF files. Defaults to None.
        ignore (Optional[List[str]]):
            List of filename codes to ignore.
            Defaults to ["Merge"], which is a
            code for merged images.

    Returns:
        str: Path to the output OME-TIFF file.
    """

    # except on dir already existing
    if pathlib.Path(output_path).is_file():
        raise FileExistsError(
            (
                f"Output path {output_path} already exists."
                "Please remove before creating a new OME-TIFF."
            )
        )

    if not pathlib.Path(image_dir).is_dir():
        raise NotADirectoryError(f"Image directory {image_dir} does not exist.")

    frame_zstacks = image_set_to_arrays(
        image_dir=image_dir, label_dir=label_dir, channel_map=channel_map, ignore=ignore
    )

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
            label_names.append(compartment_name)

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
        # due to tifffile limitations
        "PhysicalSizeXUnit": "um",
        "PhysicalSizeYUnit": "um",
        "PhysicalSizeZUnit": "um",
        "Channel": [{"Name": name} for name in combined_channel_names],
    }
    ome_xml = generate_ome_xml(ome_metadata)

    # Write the combined data to a single OME-TIFF
    with tiff.TiffWriter(output_path, bigtiff=True) as tif:
        tif.write(combined_data, description=ome_xml, photometric="minisblack")

    return output_path
