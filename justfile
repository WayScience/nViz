# justfile for common project commands
# see here for more information: https://github.com/casey/just

# find system default shell
hashbang := if os() == 'macos' {
	'/usr/bin/env zsh'
} else {
	'/usr/bin/env bash'
}

# show a list of just commands for this project
default:
  @just --list

# install the project for development purposes
@setup:
    #!{{hashbang}}
    uv pip install '.'

# run testing on development source
@test:
    #!{{hashbang}}
    uv run pre-commit run -a
    uv run pytest

# run tiff to omezarr example with real data
@tiff_to_zarr:
    #!{{hashbang}}
    uv run python src/raw_organoid_images_to_omezarr/tiff_to_omezarr.py

@tiff_to_ometiff:
    #!{{hashbang}}
    uv run python src/raw_organoid_images_to_omezarr/tiff_to_ometiff.py

@tiff_to_ometiff_to_napari:
    #!{{hashbang}}
    uv run python src/raw_organoid_images_to_omezarr/tiff_to_ometiff.py
    uv run python src/raw_organoid_images_to_omezarr/ometiff_to_napari.py

@tiff_to_ometiff_to_avivator:
    #!{{hashbang}}
    uv run python src/raw_organoid_images_to_omezarr/tiff_to_ometiff.py
    uv run python src/raw_organoid_images_to_omezarr/ometiff_to_avivator.py

@tiff_to_zarr_napari:
    #!{{hashbang}}
    uv run python src/raw_organoid_images_to_omezarr/tiff_to_omezarr.py
    uv run python src/raw_organoid_images_to_omezarr/zarr_to_napari.py

@tiff_to_zarr_neuroglancer:
    #!{{hashbang}}
    uv run python src/raw_organoid_images_to_omezarr/tiff_to_omezarr.py
    uv run python src/raw_organoid_images_to_omezarr/zarr_to_neuroglancer.py

# run tiff to omezarr example with randomized data
@randomized_to_omezarr:
    #!{{hashbang}}
    uv run python src/raw_organoid_images_to_omezarr/randomized_to_omezarr.py
