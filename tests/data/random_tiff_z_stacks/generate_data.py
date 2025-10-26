"""
Generates example z-stack TIFF files with randomized data for testing.
"""

import pathlib
from typing import List, Tuple

import numpy as np
import tifffile as tiff

channels = ["Channel A", "Channel B", "Channel C", "Channel D", "Channel E"]
channels_map = {
    "Channel A": "111",
    "Channel B": "222",
    "Channel C": "333",
    "Channel D": "444",
    "Channel E": "555",
}

relpath = pathlib.Path(__file__).parent
scaling_values = (1.0, 0.1, 0.1)  # (z, y, x) microns per voxel
num_z_slices = 48
image_shape = (128, 128)


def create_ellipsoid_mask(
    shape_zyx: Tuple[int, int, int],
    center_zyx: Tuple[int, int, int],
    radii_zyx_vox: Tuple[float, float, float],
) -> np.ndarray:
    """Return a binary ellipsoid mask inside the given shape."""
    z, y, x = np.indices(shape_zyx)
    dz = (z - center_zyx[0]) / radii_zyx_vox[0]
    dy = (y - center_zyx[1]) / radii_zyx_vox[1]
    dx = (x - center_zyx[2]) / radii_zyx_vox[2]
    return (dz**2 + dy**2 + dx**2) <= 1.0


def create_labeled_spheres_volume(
    shape_zyx: Tuple[int, int, int],
    scales_zyx: Tuple[float, float, float],
    n_spheres: int = 24,
    radius_um: float = 1.6,
    seed: int = 11,
    margin_um: Tuple[float, float, float] = (2.0, 3.0, 3.0),
) -> np.ndarray:
    """Create a volume with physically spherical labeled blobs (1, 2, 3...)."""
    Z, Y, X = shape_zyx
    sz, sy, sx = scales_zyx

    # Convert physical dimensions (µm) → voxel radii
    r_vox = (radius_um / sz, radius_um / sy, radius_um / sx)
    margin_zyx = (
        int(np.ceil(margin_um[0] / sz)),
        int(np.ceil(margin_um[1] / sy)),
        int(np.ceil(margin_um[2] / sx)),
    )

    vol = np.zeros(shape_zyx, dtype=np.uint16)
    rng = np.random.default_rng(seed)
    centers: List[Tuple[int, int, int]] = []

    sep_zyx = (int(2 * r_vox[0]) + 1, int(2 * r_vox[1]) + 1, int(2 * r_vox[2]) + 1)

    attempts = 0
    max_attempts = n_spheres * 100
    # try to add spheres until we reach the desired number
    # or exceed max attempts
    while len(centers) < n_spheres and attempts < max_attempts:
        attempts += 1
        cz = rng.integers(margin_zyx[0], max(margin_zyx[0] + 1, Z - margin_zyx[0]))
        cy = rng.integers(margin_zyx[1], max(margin_zyx[1] + 1, Y - margin_zyx[1]))
        cx = rng.integers(margin_zyx[2], max(margin_zyx[2] + 1, X - margin_zyx[2]))

        ok = True
        for pz, py, px in centers:
            if (
                abs(cz - pz) < sep_zyx[0]
                and abs(cy - py) < sep_zyx[1]
                and abs(cx - px) < sep_zyx[2]
            ):
                ok = False
                break
        if not ok:
            continue
        centers.append((int(cz), int(cy), int(cx)))

    # Label each sphere uniquely
    label_val = 1
    for cz, cy, cx in centers:
        mask = create_ellipsoid_mask(shape_zyx, (cz, cy, cx), r_vox)
        vol[mask] = label_val
        label_val += 1

    return vol


shape_zyx = (num_z_slices, *image_shape)
compartment = create_labeled_spheres_volume(
    shape_zyx,
    scales_zyx=scaling_values,
    n_spheres=24,
    radius_um=1.6,  # physical sphere radius in µm
    seed=11,
)
label_mask = compartment > 0

output_dir = relpath / "Z99"
output_dir.mkdir(exist_ok=True)

# Create image stack with static inside labels only
for channel in channels:
    ch_seed = abs(hash(channel)) % (2**32)
    ch_rng = np.random.default_rng(ch_seed)
    for z in range(num_z_slices):
        noise = ch_rng.integers(0, 4096, size=image_shape, dtype=np.uint16)
        z_slice = np.where(label_mask[z], noise, 0).astype(np.uint16)
        filename = f"Z99_{channels_map[channel]}_ZS{z:03d}.tif"
        tiff.imwrite(output_dir / filename, z_slice)

print(f"TIFF files written to {output_dir}")

# Write label volume with unique sphere IDs
label_path = output_dir.parent / "labels"
label_path.mkdir(exist_ok=True)
ij_meta = {"spacing": float(scaling_values[0]), "unit": "um"}

tiff.imwrite(
    label_path / "compartment.tif",
    compartment.astype(np.uint16),
    photometric="minisblack",
    imagej=True,
    metadata=ij_meta,
)

print("Wrote labels/compartment.tif (labeled physical spheres)")

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
