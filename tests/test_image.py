"""
Tests for the image module.
"""

import pathlib
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pytest
import tifffile as tiff
import zarr

from nviz.image import image_set_to_arrays, tiff_to_ometiff, tiff_to_zarr
from tests.utils import example_data_for_image_tests


@pytest.mark.parametrize(
    (
        "image_dir, label_dir, output_path, channel_map, "
        "scaling_values, ignore, expected_labels"
    ),
    example_data_for_image_tests,
)
def test_image_set_to_arrays(
    image_dir: str,
    label_dir: Optional[str],
    output_path: str,
    channel_map: Dict[str, str],
    scaling_values: Tuple[int, int, int],
    ignore: Optional[List[str]],
    expected_labels: List[str],
):
    # Call the function
    result = image_set_to_arrays(
        image_dir=image_dir, label_dir=label_dir, channel_map=channel_map, ignore=ignore
    )

    # check that we have all keys
    if ignore is None:
        all(channel not in result["images"] for channel in channel_map.values())

    # check that we ignored what we should have
    elif ignore is not None:
        assert all(ignored not in result["images"] for ignored in ignore)


@pytest.mark.parametrize(
    (
        "image_dir, label_dir, output_path, channel_map, "
        "scaling_values, ignore, expected_labels"
    ),
    example_data_for_image_tests,
)
def test_tiff_to_zarr(
    image_dir: str,
    label_dir: Optional[str],
    output_path: str,
    channel_map: Dict[str, str],
    scaling_values: Tuple[int, int, int],
    ignore: Optional[List[str]],
    expected_labels: List[str],
    tmp_path: pathlib.Path,
):
    """
    Tests the tiff_to_zarr function.
    """

    output_path = tiff_to_zarr(
        image_dir=image_dir,
        label_dir=label_dir,
        output_path=f"{tmp_path}/{output_path}",
        channel_map=channel_map,
        scaling_values=scaling_values,
        ignore=ignore,
    )

    # Check if the output path exists
    assert Path(output_path).exists()

    # Check if the Zarr structure is correct
    zarr_root = zarr.open(output_path, mode="r")
    assert "images" in list(zarr_root.keys())

    # check if we have labels if we supplied them
    if label_dir is not None:
        assert "labels" in zarr_root

    for channel in channel_map.values():
        if ignore is not None and channel not in [
            channel_map[ignored] for ignored in ignore
        ]:
            assert channel in list(zarr_root["images"])

    # check if we have labels if we supplied them
    if label_dir is not None:
        assert all(
            expected_label in list(zarr_root["labels"].keys())
            for expected_label in expected_labels
        )


@pytest.mark.parametrize(
    (
        "image_dir, label_dir, output_path, channel_map, "
        "scaling_values, ignore, expected_labels"
    ),
    example_data_for_image_tests,
)
def test_tiff_to_ometiff(
    image_dir: str,
    label_dir: Optional[str],
    output_path: str,
    channel_map: Dict[str, str],
    scaling_values: Tuple[int, int, int],
    ignore: Optional[List[str]],
    expected_labels: List[str],
    tmp_path: pathlib.Path,
):
    """
    Tests the tiff_to_ometiff function.
    """

    output_path = tiff_to_ometiff(
        image_dir=image_dir,
        label_dir=label_dir,
        output_path=f"{tmp_path}/{output_path}",
        channel_map=channel_map,
        scaling_values=scaling_values,
        ignore=ignore,
    )

    # Check if the output path exists
    assert Path(output_path).exists()

    # Read the OME-TIFF file and check its contents
    with tiff.TiffFile(output_path) as tif:
        assert len(tif.pages) > 0
        metadata = tif.ome_metadata
        assert metadata is not None

        # Parse the OME-XML metadata
        root = ET.fromstring(metadata)
        channels = root.find(
            ".//{http://www.openmicroscopy.org/Schemas/OME/2016-06}Pixels"
        ).findall("{http://www.openmicroscopy.org/Schemas/OME/2016-06}Channel")

        # Check the metadata for channels
        for channel in channel_map.values():
            if ignore is not None and channel not in [
                channel_map[ignored] for ignored in ignore
            ]:
                assert any(channel == ch.get("Name") for ch in channels)

        # Check the metadata for physical sizes
        pixels = root.find(
            ".//{http://www.openmicroscopy.org/Schemas/OME/2016-06}Pixels"
        )
        assert pixels.get("PhysicalSizeX") == str(scaling_values[2])
        assert pixels.get("PhysicalSizeY") == str(scaling_values[1])
        assert pixels.get("PhysicalSizeZ") == str(scaling_values[0])
