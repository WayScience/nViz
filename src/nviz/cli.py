"""
CLI for nviz
"""

from typing import Dict, List, Optional, Tuple, Union

import fire

from nviz.image import tiff_to_ometiff, tiff_to_zarr
from nviz.view import view_ometiff_with_napari, view_zarr_with_napari


class nVizCLI:
    def tiff_to_zarr(  # noqa: PLR0913
        self,
        image_dir: str,
        output_path: str,
        channel_map: Dict[str, str],
        scaling_values: Union[List[int], Tuple[int]],
        label_dir: Optional[str] = None,
        ignore: Optional[List[str]] = ["Merge"],
    ) -> str:
        """
        CLI interface for converting TIFF images to Zarr format.

        Args:
            image_dir (str):
                Directory containing TIFF image files.
            output_path (str):
                Path to save the output OME-Zarr file.
            channel_map (Dict[str, str]):
                Mapping from filename codes to channel names.
            scaling_values (Union[List[int], Tuple[int]]):
                Scaling values for the images.
            label_dir (Optional[str]):
                Directory containing label TIFF files. Defaults to None.
            ignore (Optional[List[str]]):
                List of filename codes to ignore.
                Defaults to ["Merge"], which is a
                code for merged images.

        Returns:
            str: Path to the output OME-Zarr file.
        """

        return tiff_to_zarr(
            image_dir=image_dir,
            output_path=output_path,
            channel_map=channel_map,
            scaling_values=scaling_values,
            label_dir=label_dir,
            ignore=ignore,
        )

    def tiff_to_ometiff(  # noqa: PLR0913
        self,
        image_dir: str,
        output_path: str,
        channel_map: Dict[str, str],
        scaling_values: Union[List[int], Tuple[int]],
        label_dir: Optional[str] = None,
        ignore: Optional[List[str]] = ["Merge"],
    ) -> str:
        """
        CLI interface for converting TIFF images to OME-TIFF format.

        Args:
            image_dir (str):
                Directory containing TIFF image files.
            output_path (str):
                Path to save the output OME-Zarr file.
            channel_map (Dict[str, str]):
                Mapping from filename codes to channel names.
            scaling_values (Union[List[int], Tuple[int]]):
                Scaling values for the images.
            label_dir (Optional[str]):
                Directory containing label TIFF files. Defaults to None.
            ignore (Optional[List[str]]):
                List of filename codes to ignore.
                Defaults to ["Merge"], which is a
                code for merged images.

        Returns:
            str: Path to the output OME-TIFF file.
        """

        return tiff_to_ometiff(
            image_dir=image_dir,
            output_path=output_path,
            channel_map=channel_map,
            scaling_values=scaling_values,
            label_dir=label_dir,
            ignore=ignore,
        )

    def view_zarr(
        self,
        zarr_dir: str,
        scaling_values: Union[List[int], Tuple[int]],
        headless: Optional[bool] = False,
    ) -> Optional[str]:
        """
        CLI interface for viewing Zarr files with napari.

        Args:
            zarr_dir (str):
                Path to the Zarr file.
            scaling_values (Union[List[int], Tuple[int]]):
                Scaling values for the image.
            headless (Optional[bool]):
                Whether to run in headless mode
                (where we don't run napari and hand
                back the viewer object instead).
                Defaults to False.

        Returns:
            Optional[str]:
                The napari viewer object if not headless,
                otherwise None.
        """

        return view_zarr_with_napari(
            zarr_dir=zarr_dir, scaling_values=scaling_values, headless=headless
        )

    def view_ometiff(
        self,
        ometiff_path: str,
        scaling_values: Union[List[int], Tuple[int]],
        headless: Optional[bool] = False,
    ) -> Optional[str]:
        """
        CLI interface for viewing OME-TIFF files with napari.

        Args:
            ometiff_path (str):
                Path to the OME-TIFF file.
            scaling_values (Union[List[int], Tuple[int]]):
                Scaling values for the image.
            headless (Optional[bool]):
                Whether to run in headless mode
                (where we don't run napari and hand
                back the viewer object instead).
                Defaults to False.

        Returns:
            Optional[str]:
                The napari viewer object if not headless,
                otherwise None.
        """

        return view_ometiff_with_napari(
            ometiff_path=ometiff_path, scaling_values=scaling_values, headless=headless
        )


def trigger() -> None:
    """
    Trigger the CLI to run.
    """
    fire.Fire(nVizCLI)
