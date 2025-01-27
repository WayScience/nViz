"""
Utilities for viewing n-dimensional data
"""

import logging
from typing import Optional

import napari
import tifffile as tiff
import xmltodict
import zarr

logger = logging.getLogger(__name__)


def view_zarr_with_napari(
    zarr_dir: str, scaling_values: tuple, headless: bool = False
) -> Optional[napari.Viewer]:
    """
    View a Zarr file created with nviz through napari.

    Args:
        zarr_dir (str):
            The path to the Zarr file.
        scaling_values (tuple):
            The scaling values for the image.
        headless (bool):
            Whether to run in headless mode
            (where we don't run napari and hand
            back the viewer object instead).

    Returns:
        Optional[napari.Viewer]]:
            The napari viewer object if not headless,
            otherwise None.
    """
    # Check Zarr file structure
    frame_zarr = zarr.open(zarr_dir, mode="r")

    # Visualize with napari, start in 3d mode
    viewer = napari.Viewer(ndisplay=3)

    # Iterate through each channel in the Zarr file
    for channel_name in sorted(frame_zarr["images"].keys(), reverse=True):
        viewer.add_image(
            frame_zarr["images"][channel_name]["0"][:],
            name=channel_name,
            scale=scaling_values,
        )

    # Iterate through each compartment in the Zarr file and add labels to Napari
    if "labels" in frame_zarr:
        for label_name in sorted(frame_zarr["labels"].keys(), reverse=True):
            viewer.add_labels(
                frame_zarr["labels"][label_name]["0"][:],
                name=f"{label_name}",
                scale=scaling_values,
            )

    if not headless:
        # Start the Napari event loop
        napari.run()
    else:
        logger.warning(
            "Running view in headless mode and returning a napari viewer object."
        )

    # otherwise return the viewer
    return viewer


def view_ometiff_with_napari(
    ometiff_path: str, scaling_values: tuple, headless: bool = False
) -> Optional[napari.Viewer]:
    """
    View a OME-TIFF file created with nviz through napari.

    Args:
        ometiff_path (str):
            The path to the OME-TIFF file.
        scaling_values (tuple):
            The scaling values for the image.
        headless (bool):
            Whether to run in headless mode
            (where we don't run napari and hand
            back the viewer object instead).

    Returns:
        Optional[napari.Viewer]]:
            The napari viewer object if not headless,
            otherwise None.
    """

    # Visualize with napari, start in 3d mode
    viewer = napari.Viewer(ndisplay=3)

    # Read and add layers from the combined OME-TIFF file
    with tiff.TiffFile(ometiff_path) as tif:
        combined_data = tif.asarray()
        metadata = xmltodict.parse(tif.ome_metadata)
        channel_names = [
            channel["@Name"]
            for channel in metadata["OME"]["Image"]["Pixels"]["Channel"]
        ]

        # First, add image layers
        for i, (channel_data, channel_name) in enumerate(
            zip(combined_data, channel_names)
        ):
            if "(labels)" not in channel_name:
                viewer.add_image(
                    channel_data,
                    name=channel_name,
                    scale=scaling_values,
                )

        # Then, add label layers
        for i, (channel_data, channel_name) in enumerate(
            zip(combined_data, channel_names)
        ):
            if "(labels)" in channel_name:
                viewer.add_labels(
                    channel_data,
                    name=channel_name,
                    scale=scaling_values,
                )

    if not headless:
        # Start the Napari event loop
        napari.run()
    else:
        logger.warning(
            "Running view in headless mode and returning a napari viewer object."
        )

    # otherwise return the viewer
    return viewer
