"""
Tests CLI capabilities for nviz
"""

import pytest

from tests.utils import run_cli_command


def test_cli_util():
    """
    Test the run_cli_command for successful output
    """

    _, _, returncode = run_cli_command(["echo", "'hello world'"])

    assert returncode == 0

    assert returncode == 0


@pytest.mark.parametrize(
    "image_dir, output_path, channel_map, scaling_values, label_dir, ignore",
    [
        (
            "tests/data/random_tiff_z_stacks/Z99",
            "output.zarr",
            (
                '{ "111": "Channel A", "222": "Channel B", "333": "Channel C",'
                ' "444": "Channel D", "555": "Channel E", }'
            ),
            "(1.0, 0.1, 0.1)",
            "None",
            "None",
        )
    ],
)
def test_cli_tiff_to_zarr(
    tmp_path, image_dir, output_path, channel_map, scaling_values, label_dir, ignore
):
    """
    Test CLI use of tiff to zarr and viewing capabilities
    """
    stdout, _, returncode = run_cli_command(
        [
            "nviz",
            "tiff_to_zarr",
            image_dir,
            (output_path := f"{tmp_path}/{output_path}"),
            channel_map,
            scaling_values,
            label_dir,
            ignore,
        ]
    )

    assert returncode == 0
    assert stdout.strip() == output_path

    stdout, stderr, returncode = run_cli_command(
        ["nviz", "view_zarr", output_path, scaling_values, "True"]
    )

    # napari has difficulties when used headlessly through the cli
    # so we check that the output shows we returned a viewer object.
    # This isn't a typical usecase because we can't use the viewer
    # object through a CLI interface (we only enable it for testing).
    assert stdout.strip() == "napari.Viewer: napari"


@pytest.mark.parametrize(
    "image_dir, output_path, channel_map, scaling_values, label_dir, ignore",
    [
        (
            "tests/data/random_tiff_z_stacks/Z99",
            "output.zarr",
            (
                '{ "111": "Channel A", "222": "Channel B", "333": "Channel C",'
                ' "444": "Channel D", "555": "Channel E", }'
            ),
            "(1.0, 0.1, 0.1)",
            "None",
            "None",
        )
    ],
)
def test_cli_tiff_to_ometiff(
    tmp_path, image_dir, output_path, channel_map, scaling_values, label_dir, ignore
):
    """
    Test CLI use of tiff to ome-tiff and viewing capabilities
    """
    stdout, _, returncode = run_cli_command(
        [
            "nviz",
            "tiff_to_ometiff",
            image_dir,
            (output_path := f"{tmp_path}/{output_path}"),
            channel_map,
            scaling_values,
            label_dir,
            ignore,
        ]
    )

    assert returncode == 0
    assert stdout.strip() == output_path

    stdout, _, returncode = run_cli_command(
        ["nviz", "view_ometiff", output_path, scaling_values, "True"]
    )

    # napari has difficulties when used headlessly through the cli
    # so we check that the output shows we returned a viewer object.
    # This isn't a typical usecase because we can't use the viewer
    # object through a CLI interface (we only enable it for testing).
    assert stdout.strip() == "napari.Viewer: napari"
