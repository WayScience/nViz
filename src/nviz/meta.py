"""
Viewing utilities for GFF 3D organoid project
"""

import re
import xml.etree.ElementTree as ET
from typing import Dict, Optional, Tuple
from xml.etree.ElementTree import Element, SubElement, tostring


def extract_z_slice_number_from_filename(filename: str) -> int:
    """
    Extracts a z-slice number from a filename.
    Follows conventions from images which are produced
    to our knowledge by ZEISS LSM 880 with Airyscan
    microscope output.

    Assumes the z-slice number
    is a zero-padded number in the filename
    with the pattern '_ZS###_'.

    Args:
        filename (str):
            The name of the file from which to extract the z-slice number.

    Returns:
        int:
            The extracted z-slice number. Returns 0 if the pattern is not found.
    """
    match = re.search(r"_ZS(\d+)_", filename)
    return int(match.group(1)) if match else 0


def gather_scaling_info_from_scaninfoxml(
    xml_file: str,
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Reads the scan information from an XML file and
    returns the values of ZStackSpacingMicrons,
    MicronsPerPixelY, and MicronsPerPixelX.

    This function specifically caters to a file named
    ScanInfo.xml which is included to our knowledge within
    ZEISS LSM 880 with Airyscan microscope output (and perhaps
    others).

    Args:
        xml_file (str):
            Path to the XML file.

    Returns:
        Tuple[Optional[float], Optional[float], Optional[float]]:
            A tuple containing the values of
            ZStackSpacingMicrons, MicronsPerPixelY,
            and MicronsPerPixelX. If a value is not found,
            it will be None.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    microns_per_pixel_y: Optional[float] = None
    microns_per_pixel_x: Optional[float] = None
    z_stack_spacing_microns: Optional[float] = None

    for setting in root.findall(".//Setting"):
        param = setting.get("Parameter")
        if param == "MicronsPerPixelY":
            microns_per_pixel_y = float(setting.text)
        elif param == "MicronsPerPixelX":
            microns_per_pixel_x = float(setting.text)
        elif param == "ZStackSpacingMicrons":
            z_stack_spacing_microns = float(setting.text)

    return (z_stack_spacing_microns, microns_per_pixel_y, microns_per_pixel_x)


def generate_ome_xml(metadata: Dict) -> str:
    """
    Generate OME-XML metadata for use within an OME-TIFF file.

    Args:
        metadata (Dict): Dictionary containing metadata.

    Returns:
        str: OME-XML string.
    """
    ome = Element("OME", xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06")
    image = SubElement(ome, "Image", ID="Image:0")
    pixels = SubElement(
        image,
        "Pixels",
        {
            "ID": "Pixels:0",
            "Type": "uint16",
            "DimensionOrder": "CZYX",
            "SizeC": str(metadata["SizeC"]),
            "SizeZ": str(metadata["SizeZ"]),
            "SizeY": str(metadata["SizeY"]),
            "SizeX": str(metadata["SizeX"]),
            "PhysicalSizeX": str(metadata["PhysicalSizeX"]),
            "PhysicalSizeY": str(metadata["PhysicalSizeY"]),
            "PhysicalSizeZ": str(metadata["PhysicalSizeZ"]),
            "PhysicalSizeXUnit": metadata["PhysicalSizeXUnit"],
            "PhysicalSizeYUnit": metadata["PhysicalSizeYUnit"],
            "PhysicalSizeZUnit": metadata["PhysicalSizeZUnit"],
        },
    )
    for i, channel in enumerate(metadata["Channel"]):
        SubElement(
            pixels,
            "Channel",
            {
                "ID": f"Channel:0:{i}",
                "Name": channel["Name"],
            },
        )
    return tostring(ome, encoding="unicode")
