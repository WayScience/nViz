"""
Read OME-TIFF files from this project into Napari
"""

import pathlib
import pprint

import napari
import tifffile as tiff
import xmltodict

from gff3d_utils.view import gather_scaling_info_from_scaninfoxml

# gather relative path for this file
relpath = pathlib.Path(__file__).parent

# Define the output path for the combined OME-TIFF file
combined_output_path = f"{relpath}/data/example_output.ome.tiff"

# scaninfo file
scaninfo_file = pathlib.Path(
    f"{relpath}/data/GFF-data/originals/NF0014-Thawed 3 (Raw image files)-Combined"
    "/C10-1/ScanInfo.xml"
)

# gather scaling details
scaling_values = gather_scaling_info_from_scaninfoxml(scaninfo_file)

# Visualize with napari, start in 3d mode
viewer = napari.Viewer(ndisplay=3)

# Read and add layers from the combined OME-TIFF file
with tiff.TiffFile(combined_output_path) as tif:
    combined_data = tif.asarray()
    metadata = xmltodict.parse(tif.ome_metadata)
    pprint.pprint(metadata)  # Print the metadata to understand its structure
    channel_names = [
        channel["@Name"] for channel in metadata["OME"]["Image"]["Pixels"]["Channel"]
    ]

    # First, add image layers
    for i, (channel_data, channel_name) in enumerate(zip(combined_data, channel_names)):
        if "(labels)" not in channel_name:
            viewer.add_image(
                channel_data,
                name=channel_name,
                scale=scaling_values,
            )

    # Then, add label layers
    for i, (channel_data, channel_name) in enumerate(zip(combined_data, channel_names)):
        if "(labels)" in channel_name:
            viewer.add_labels(
                channel_data,
                name=channel_name,
                scale=scaling_values,
            )

# Start the Napari event loop
napari.run()
