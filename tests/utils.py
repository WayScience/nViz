"""
Utilities for testing.
"""

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
            None
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
            ["compartment (labels)"]
        ),
    ]