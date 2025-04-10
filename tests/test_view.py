"""
Tests for the view module
"""

import pathlib
from typing import Dict, List, Optional, Tuple

import pytest

from nviz.image import tiff_to_ometiff, tiff_to_zarr
from nviz.view import view_ometiff_with_napari, view_zarr_with_napari
from tests.utils import (
    example_data_for_image_tests,
    real_data_for_image_tests,
    skip_if_no_synapse_token,
)


@pytest.mark.parametrize(
    (
        "image_dir, label_dir, output_path, channel_map, "
        "scaling_values, ignore, expected_labels"
    ),
    example_data_for_image_tests,
)
def test_view_zarr_with_napari_and_example_data(
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
    Tests the view_zarr_with_napari function.
    """

    zarr_dir = tiff_to_zarr(
        image_dir=image_dir,
        label_dir=label_dir,
        output_path=f"{tmp_path}/{output_path}",
        channel_map=channel_map,
        scaling_values=scaling_values,
        ignore=ignore,
    )

    # Call the function
    view = view_zarr_with_napari(
        zarr_dir=zarr_dir, scaling_values=scaling_values, headless=True
    )

    # close the view
    view.close()


@pytest.mark.parametrize(
    (
        "image_dir, label_dir, output_path, channel_map, "
        "scaling_values, ignore, expected_labels"
    ),
    example_data_for_image_tests,
)
def test_view_ometiff_with_napari_and_example_data(
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
    Tests the view_ometiff_with_napari_and_example_data function.
    """

    ometiff_path = tiff_to_ometiff(
        image_dir=image_dir,
        label_dir=label_dir,
        output_path=f"{tmp_path}/{output_path}",
        channel_map=channel_map,
        scaling_values=scaling_values,
        ignore=ignore,
    )

    # Call the function
    view = view_ometiff_with_napari(
        ometiff_path=ometiff_path,
        scaling_values=scaling_values,
        headless=True,
    )

    # close the view
    view.close()


@skip_if_no_synapse_token
@pytest.mark.parametrize(
    (
        "image_dir, label_dir, output_path, channel_map, "
        "scaling_values, ignore, expected_labels"
    ),
    real_data_for_image_tests,
)
def test_view_zarr_with_napari_and_real_data(
    image_dir: str,
    label_dir: Optional[str],
    output_path: str,
    channel_map: Dict[str, str],
    scaling_values: Tuple[int, int, int],
    ignore: Optional[List[str]],
    expected_labels: List[str],
    tmp_path: pathlib.Path,
    ensure_synapse_data: pathlib.Path,
):
    """
    Tests the view_zarr_with_napari_and_real_data function.
    """

    zarr_dir = tiff_to_zarr(
        image_dir=image_dir,
        label_dir=label_dir,
        output_path=f"{tmp_path}/{output_path}",
        channel_map=channel_map,
        scaling_values=scaling_values,
        ignore=ignore,
    )

    # Call the function
    view = view_zarr_with_napari(
        zarr_dir=zarr_dir, scaling_values=scaling_values, headless=True
    )

    # close the view
    view.close()


@skip_if_no_synapse_token
@pytest.mark.parametrize(
    (
        "image_dir, label_dir, output_path, channel_map, "
        "scaling_values, ignore, expected_labels"
    ),
    real_data_for_image_tests,
)
def test_view_ometiff_with_napari_and_real_data(
    image_dir: str,
    label_dir: Optional[str],
    output_path: str,
    channel_map: Dict[str, str],
    scaling_values: Tuple[int, int, int],
    ignore: Optional[List[str]],
    expected_labels: List[str],
    tmp_path: pathlib.Path,
    ensure_synapse_data: pathlib.Path,
):
    """
    Tests the view_ometiff_with_napari function.
    """

    ometiff_path = tiff_to_ometiff(
        image_dir=image_dir,
        label_dir=label_dir,
        output_path=f"{tmp_path}/{output_path}",
        channel_map=channel_map,
        scaling_values=scaling_values,
        ignore=ignore,
    )

    # Call the function
    view = view_ometiff_with_napari(
        ometiff_path=ometiff_path,
        scaling_values=scaling_values,
        headless=True,
    )

    # close the view
    view.close()
