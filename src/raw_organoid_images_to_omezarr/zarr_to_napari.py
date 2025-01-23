"""
Read a Zarr file from this project into Napari
"""

import pathlib

import napari
import zarr

from gff3d_utils.view import (
    gather_scaling_info_from_scaninfoxml,
)

# gather relative path for this file
relpath = pathlib.Path(__file__).parent

# Define the output path
output_path = f"{relpath}/data/example_output.zarr"

# scaninfo file
scaninfo_file = pathlib.Path(
    f"{relpath}/data/GFF-data/originals/NF0014-Thawed 3 (Raw image files)-Combined"
    "/C10-1/ScanInfo.xml"
)

# gather scaling details
scaling_values = gather_scaling_info_from_scaninfoxml(scaninfo_file)

# Check Zarr file structure
frame_zarr = zarr.open(output_path, mode="r")
print(frame_zarr.tree())

# Visualize with napari, start in 3d mode
viewer = napari.Viewer(ndisplay=3)

# Iterate through each channel in the Zarr file
for channel_name in sorted(frame_zarr["images"].keys(), reverse=True):
    print(f"Opening {channel_name} in Napari...")
    viewer.add_image(
        frame_zarr["images"][channel_name]["0"][:],
        name=channel_name,
        scale=scaling_values,
    )

# Iterate through each compartment in the Zarr file and add labels to Napari
for label_name in sorted(frame_zarr["labels"].keys(), reverse=True):
    print(f"Opening {label_name} in Napari...")
    viewer.add_labels(
        frame_zarr["labels"][label_name]["0"][:],
        name=f"{label_name} (label)",
        scale=scaling_values,
    )

# Start the Napari event loop
napari.run()
