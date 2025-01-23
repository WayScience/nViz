# nVis

This project focuses on ingesting a set of [TIFF](https://en.wikipedia.org/wiki/TIFF) images as [OME-Zarr](https://pmc.ncbi.nlm.nih.gov/articles/PMC9980008/) or OME-TIFF () which are organized by channel and z-slices which compose three dimensional microscopy data for biological objects (such as organoids).
We read the output with [Napari](https://napari.org/dev/index.html), which provides a way to analyze and understand the 3D image data.

## Development

1. [Install `uv`](https://docs.astral.sh/uv/getting-started/installation/).
1. Install package locally (e.g. `uv pip install -e "."`).
