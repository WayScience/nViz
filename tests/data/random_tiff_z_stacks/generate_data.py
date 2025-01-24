"""
Generates example z-stack TIFF files with randomized data for testing.
"""

import pathlib
from typing import Tuple

import numpy as np
import tifffile as tiff

# human readable channel names
channels = [
    "Channel A",
    "Channel B",
    "Channel C",
    "Channel D",
    "Channel E",
]

# map human readable channel names to machine ones
# which simulate what is produced by the microscope
# or teams who create images.
channels_map = {
    "Channel A": "111",
    "Channel B": "222",
    "Channel C": "333",
    "Channel D": "444",
    "Channel E": "555",
}

# gather a relative path
relpath = pathlib.Path(__file__).parent

# Set common static scaling values
scaling_values = (1.0, 0.1, 0.1)  # (z, y, x) in microns

# Generate random data for z-slices
num_z_slices = 10
image_shape = (100, 100)  # Example shape, adjust as needed

# create random data for each channel
channels = {
    channel: [
        np.random.randint(0, 65535, size=image_shape, dtype=np.uint16)
        for _ in range(num_z_slices)
    ]
    for channel in channels
}

# Debug: show channel keys and file counts
print(channels.keys())
for channel, files in channels.items():
    print(f"Channel: {channel}, Slices: {len(files)}")

# Define the output directory
output_dir = relpath / "Z99"
pathlib.Path(output_dir).mkdir(exist_ok=True)

# Write each z-slice as a separate TIFF file
for channel, z_slices in channels.items():
    for z_index, z_slice in enumerate(z_slices):
        filename = f"Z99_{channels_map[channel]}_ZS{z_index:03d}.tif"
        filepath = output_dir / filename
        tiff.imwrite(filepath, z_slice)

print(f"TIFF files written to {output_dir}")


# Create a single multidimensional TIFF file with sphere shapes
def create_sphere_image(
    shape: Tuple[int, int, int], radius: int, center: Tuple[int, int, int]
) -> np.ndarray:
    """Create a 3D image with a sphere.

    Args:
        shape (Tuple[int, int, int]): The shape of the 3D image (z, y, x).
        radius (int): The radius of the sphere.
        center (Tuple[int, int, int]): The center of the sphere (z, y, x).

    Returns:
        np.ndarray: A 3D image with a sphere.
    """
    z, y, x = np.indices(shape)
    distance = np.sqrt(
        (z - center[0]) ** 2 + (y - center[1]) ** 2 + (x - center[2]) ** 2
    )
    sphere = (distance <= radius).astype(np.uint16) * 65535
    return sphere


sphere_radius = 20
sphere_center = (num_z_slices // 2, image_shape[0] // 2, image_shape[1] // 2)
sphere_image = create_sphere_image(
    (num_z_slices, *image_shape), sphere_radius, sphere_center
)

# create a path for labels
label_path = output_dir.parent / "labels"
pathlib.Path(label_path).mkdir(exist_ok=True)

# Write the sphere image as a single multidimensional TIFF file
sphere_tiff_path = label_path / "compartment.tif"
tiff.imwrite(sphere_tiff_path, sphere_image, photometric="minisblack")

print(f"Sphere TIFF file written to {sphere_tiff_path}")

scaninfo_file = relpath / "ScanInfo.xml"

with open(scaninfo_file, "w") as file:
    file.write(
        """
<?xml version="1.0" encoding="utf-8"?>
<ScanInfo>
  <Version>0.0.0.0</Version>
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
</ScanInfo>
"""
    )
