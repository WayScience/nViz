"""
Tests for gff3d_utils/view.py
"""

import pathlib
from typing import Optional, Tuple

import pytest

from gff3d_utils.view import (
    extract_z_slice_number_from_filename,
    gather_scaling_info_from_scaninfoxml,
)


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("C10-1_405_ZS034_FOV-1.tif", 34),
        ("C10-1_405_ZS018_FOV-1.tif", 18),
        ("C10-1_405_ZS039_FOV-1.tif", 39),
        ("C10-1_405_ZS043_FOV-1.tif", 43),
        ("C10-1_405_ZS033_FOV-1.tif", 33),
        ("C10-1_405_ZS027_FOV-1.tif", 27),
        ("C10-1_405_ZS006_FOV-1.tif", 6),
        ("C10-1_405_FOV-1.tif", 0),  # No ZS pattern
        ("C10-1_405_ZS_FOV-1.tif", 0),  # Incomplete ZS pattern
    ],
)
def test_extract_z_slice_number_from_filename(filename: str, expected: int):
    """
    Tests extract_z_slice_number_from_filename
    """
    assert extract_z_slice_number_from_filename(filename) == expected


@pytest.mark.parametrize(
    "xml_content, expected",
    [
        (
            """<?xml version="1.0" encoding="utf-8"?>
            <ScanInfo>
                <Group Name="Calibration">
                    <Settings>
                        <Setting Parameter="MicronsPerPixelX">0.1006</Setting>
                        <Setting Parameter="MicronsPerPixelY">0.1006</Setting>
                    </Settings>
                </Group>
                <Group Name="Experiment">
                    <Settings>
                        <Setting Parameter="ZStackSpacingMicrons">1.000</Setting>
                    </Settings>
                </Group>
            </ScanInfo>""",
            (1.000, 0.1006, 0.1006),
        ),
        (
            """<?xml version="1.0" encoding="utf-8"?>
            <ScanInfo>
                <Group Name="Calibration">
                    <Settings>
                        <Setting Parameter="MicronsPerPixelX">0.200</Setting>
                        <Setting Parameter="MicronsPerPixelY">0.200</Setting>
                    </Settings>
                </Group>
                <Group Name="Experiment">
                    <Settings>
                        <Setting Parameter="ZStackSpacingMicrons">2.000</Setting>
                    </Settings>
                </Group>
            </ScanInfo>""",
            (2.000, 0.200, 0.200),
        ),
        (
            """<?xml version="1.0" encoding="utf-8"?>
            <ScanInfo>
                <Group Name="Calibration">
                    <Settings>
                        <Setting Parameter="MicronsPerPixelX">0.300</Setting>
                    </Settings>
                </Group>
                <Group Name="Experiment">
                    <Settings>
                        <Setting Parameter="ZStackSpacingMicrons">3.000</Setting>
                    </Settings>
                </Group>
            </ScanInfo>""",
            (3.000, None, 0.300),
        ),
    ],
)
def test_gather_scaling_info_from_scaninfoxml(
    xml_content: str,
    expected: Tuple[Optional[float], Optional[float], Optional[float]],
    tmp_path: pathlib.Path,
):
    """
    Tests gather_scaling_info_from_scaninfoxml
    """

    # write a temp file
    xml_file = tmp_path / "temp_scaninfo.xml"
    xml_file.write_text(xml_content)

    # check the results
    assert gather_scaling_info_from_scaninfoxml(xml_file) == expected
