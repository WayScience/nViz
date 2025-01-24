# nViz

[![Build Status](https://github.com/WayScience/nViz/actions/workflows/run-tests.yml/badge.svg?branch=main)](https://github.com/WayScience/nViz/actions/workflows/run-tests.yml?query=branch%3Amain)
![Coverage Status](https://raw.githubusercontent.com/WayScience/nViz/main/docs/src/_static/coverage-badge.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

This project focuses on ingesting a set of [TIFF](https://en.wikipedia.org/wiki/TIFF) images as [OME-Zarr](https://pmc.ncbi.nlm.nih.gov/articles/PMC9980008/) or [OME-TIFF](https://genomebiology.biomedcentral.com/articles/10.1186/gb-2005-6-5-r47).
Each input image set[^[1]^](#image_set_ref) are organized by channel and z-slices which form four dimensional (4D) microscopy data.
These 4D microscopy data contain information for biological objects (such as organoids).

We read the output with [Napari](https://napari.org/dev/index.html), which provides a way to analyze and understand the 3D image data.

> <a name="image_set_ref">1.</a> __Image set__ is loosely defined and changes depending on the context of the data.
> Here it represents a set of images in multiple dimensions that contain information regarding the same sample.
> Each image in an imageset is paired data and must be related as such.

## Installation

Install nViz from [PyPI](https://pypi.org/project/nViz/) or from source:

```shell
# install from pypi
pip install nviz

# install directly from source
pip install git+https://github.com/WayScience/nViz.git
```

## Contributing, Development, and Testing

Please see our [contributing](https://WayScience.github.io/coSMicQC/main/contributing) documentation for more details on contributions, development, and testing.
