# nViz

[![Build Status](https://github.com/WayScience/nViz/actions/workflows/run-tests.yml/badge.svg?branch=main)](https://github.com/WayScience/nViz/actions/workflows/run-tests.yml?query=branch%3Amain)
![Coverage Status](https://raw.githubusercontent.com/WayScience/nViz/main/docs/src/_static/coverage-badge.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

This project focuses on ingesting a set of [TIFF](https://en.wikipedia.org/wiki/TIFF) images as [OME-Zarr](https://pmc.ncbi.nlm.nih.gov/articles/PMC9980008/) or OME-TIFF () which are organized by channel and z-slices which compose three dimensional microscopy data for biological objects (such as organoids).
We read the output with [Napari](https://napari.org/dev/index.html), which provides a way to analyze and understand the 3D image data.

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
