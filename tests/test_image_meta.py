"""
Tests for nviz/view.py
"""

import pathlib
from typing import Dict, List, Optional, Tuple, Union
from xml.etree.ElementTree import fromstring

import pytest

from nviz.image_meta import (
    extract_z_slice_number_from_filename,
    gather_scaling_info_from_scaninfoxml,
    generate_ome_xml,
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


@pytest.mark.parametrize(
    "metadata, expected_channels",
    [
        (
            {
                "SizeC": 3,
                "SizeZ": 10,
                "SizeY": 512,
                "SizeX": 512,
                "PhysicalSizeX": 0.1,
                "PhysicalSizeY": 0.1,
                "PhysicalSizeZ": 1.0,
                "PhysicalSizeXUnit": "um",
                "PhysicalSizeYUnit": "um",
                "PhysicalSizeZUnit": "um",
                "Channel": [
                    {"Name": "Channel A"},
                    {"Name": "Channel B"},
                    {"Name": "Channel C"},
                ],
            },
            ["Channel A", "Channel B", "Channel C"],
        ),
        (
            {
                "SizeC": 2,
                "SizeZ": 5,
                "SizeY": 256,
                "SizeX": 256,
                "PhysicalSizeX": 0.2,
                "PhysicalSizeY": 0.2,
                "PhysicalSizeZ": 2.0,
                "PhysicalSizeXUnit": "um",
                "PhysicalSizeYUnit": "um",
                "PhysicalSizeZUnit": "um",
                "Channel": [
                    {"Name": "Channel X"},
                    {"Name": "Channel Y"},
                ],
            },
            ["Channel X", "Channel Y"],
        ),
    ],
)
def test_generate_ome_xml(
    metadata: Dict[str, Union[int, str]], expected_channels: List[str]
):
    ome_xml = generate_ome_xml(metadata)

    # Parse the generated OME-XML
    root = fromstring(ome_xml)

    # Verify the Pixels attributes
    pixels = root.find(".//{http://www.openmicroscopy.org/Schemas/OME/2016-06}Pixels")
    assert pixels is not None
    assert pixels.get("SizeC") == str(metadata["SizeC"])
    assert pixels.get("SizeZ") == str(metadata["SizeZ"])
    assert pixels.get("SizeY") == str(metadata["SizeY"])
    assert pixels.get("SizeX") == str(metadata["SizeX"])
    assert pixels.get("PhysicalSizeX") == str(metadata["PhysicalSizeX"])
    assert pixels.get("PhysicalSizeY") == str(metadata["PhysicalSizeY"])
    assert pixels.get("PhysicalSizeZ") == str(metadata["PhysicalSizeZ"])
    assert pixels.get("PhysicalSizeXUnit") == metadata["PhysicalSizeXUnit"]
    assert pixels.get("PhysicalSizeYUnit") == metadata["PhysicalSizeYUnit"]
    assert pixels.get("PhysicalSizeZUnit") == metadata["PhysicalSizeZUnit"]

    # Verify the Channel names
    channels = pixels.findall(
        "{http://www.openmicroscopy.org/Schemas/OME/2016-06}Channel"
    )
    assert len(channels) == len(expected_channels)
    for i, channel in enumerate(channels):
        assert channel.get("Name") == expected_channels[i]
