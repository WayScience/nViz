"""
Tests for the image module.
"""

import os
import pathlib
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
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

    # verify per-channel z-order matches on-disk order
    def _znum(name: str) -> int:
        # digits from the 3rd underscore-separated token (handles e.g. 'ZS015')
        token = name.split("_")[2].split(".")[0]
        m = re.search(r"\d+", token)
        assert m, f"No digits found in z token for filename: {name}"
        return int(m.group())

    # invert channel_map so we can go from display name -> code
    inv_map = {v: k for k, v in channel_map.items()}

    for disp_name, got_stack in result["images"].items():
        # skip channels the user asked us to ignore
        code = inv_map.get(disp_name, disp_name)
        if ignore is not None and code in ignore:
            continue

        files = [
            f
            for f in os.scandir(image_dir)
            if (f.name.endswith(".tif") or f.name.endswith(".tiff"))
            and f.name.split("_")[1] == code
        ]
        files_sorted = sorted(files, key=lambda f: _znum(f.name))

        # Rebuild expected stack (Z, Y, X) in the sorted order
        expected_stack = np.stack(
            [tiff.imread(f.path).astype(np.uint16) for f in files_sorted]
        )

        # Ensure shapes equal (catches “ragged stack” issues)
        assert expected_stack.shape == got_stack.shape, (
            f"{disp_name}: shape mismatch; expected {expected_stack.shape}"
            f", got {got_stack.shape}"
        )

        # Ensure exact equality (confirms correct z-ordering)
        assert np.array_equal(got_stack, expected_stack), (
            f"{disp_name}: stacked data does not match expected z-order/content"
        )


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
