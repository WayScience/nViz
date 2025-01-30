"""
Utilities for testing.
"""

import numpy as np

example_data_for_checking_image_dimensionality = [
    (
        {
            "images": np.array([[[[1, 1], [1, 1]], [[1, 1], [1, 1]]]]),
            "labels": np.array([[[[1, 1], [1, 1]], [[1, 1], [1, 1]]]]),
        },
        4,
    )
]


# data examples for use with pytest parameterized tests
# (creating a data value here because it's simpler to use
# than a fixture inside parameterized tests).
example_data_for_image_tests = [
    # test example data without labels
    (
        "tests/data/random_tiff_z_stacks/Z99",
        None,
        "output.zarr",
        {
            "111": "Channel A",
            "222": "Channel B",
            "333": "Channel C",
            "444": "Channel D",
            "555": "Channel E",
        },
        (1.0, 0.1, 0.1),
        None,
        None,
    ),
    # test example data with labels
    (
        "tests/data/random_tiff_z_stacks/Z99",
        "tests/data/random_tiff_z_stacks/labels",
        "output.zarr",
        {
            "111": "Channel A",
            "222": "Channel B",
            "333": "Channel C",
            "444": "Channel D",
            "555": "Channel E",
        },
        (1.0, 0.1, 0.1),
        None,
        ["compartment (labels)"],
    ),
    # test example data with labels and ignore a channel
    (
        "tests/data/random_tiff_z_stacks/Z99",
        "tests/data/random_tiff_z_stacks/labels",
        "output.zarr",
        {
            "111": "Channel A",
            "222": "Channel B",
            "333": "Channel C",
            "444": "Channel D",
            "555": "Channel E",
        },
        (1.0, 0.1, 0.1),
        ["555"],
        ["compartment (labels)"],
    ),
]
