from pathlib import PosixPath
from typing import Optional

import ants
import numpy as np
from ants.core import ANTsImage
from rich import print


def get_coords(x: np.ndarray,
               margin: list = [8, 8, 8],
               offset: list = [0, 0, 0]) -> list:
    """Get coordinates of a given ROI, and apply a margin with offset.

    Args:
        x (np.ndarray): ROI in binary format
        margin (list, optional): margin for xyz axes. Defaults to [8, 8, 8]
        offset (list, optional): offset for xyz axes. Defaults to [0, 0, 0]

    Returns:
        list: Coordinates in xyzxyz format
    """
    ux, uy, uz = x.shape

    mask = np.where(x != 0)

    minx, maxx = int(np.min(mask[0])) + offset[0], int(np.max(
        mask[0])) + offset[0]
    miny, maxy = int(np.min(mask[1])) + offset[1], int(np.max(
        mask[1])) + offset[1]
    minz, maxz = int(np.min(mask[2])) + offset[2], int(np.max(
        mask[2])) + offset[2]

    minx = (minx - margin[0]) if (minx - margin[0]) > 0 else 0
    miny = (miny - margin[1]) if (miny - margin[1]) > 0 else 0
    minz = (minz - margin[2]) if (minz - margin[2]) > 0 else 0
    maxx = (maxx + margin[0]) if (maxx + margin[0]) < ux else ux
    maxy = (maxy + margin[1]) if (maxy + margin[1]) < uy else uy
    maxz = (maxz + margin[2]) if (maxz + margin[2]) < uz else uz

    return [minx, miny, minz, maxx, maxy, maxz]


def crop(image: ANTsImage,
         coords: list,
         output_path: Optional[PosixPath] = None,
         log_coords: bool = True,
         ri: bool = False):
    """Crop an image using coordinates.

    Args:
        image (ANTsImage): image to be cropped
        coords (list): coordinates of the ROI
        output_path (PosixPath, optional): path to save the cropped image
        log_coords (bool, optional): log the coordinates. Defaults to True.
        ri (bool): if True, return the ROI as an ANTsImage. Defaults to False.
    """
    assert all(
        [a <= b for a, b in zip(coords[:3], image.shape)]
    ), f"Coordinates {coords[:3]} out-of-range for image shape {list(image.shape)}. It may indicate a registration problem, or too big margins."
    assert all(
        [a <= b for a, b in zip(coords[3:], image.shape)]
    ), f"Coordinates {coords[3:]} out-of-range for image shape {list(image.shape)}. It may indicate a registration problem, or too big margins."

    cropped_image = ants.crop_indices(image,
                                      lowerind=coords[:3],
                                      upperind=coords[3:])

    if cropped_image.numpy().any():
        if output_path:
            ants.image_write(cropped_image, str(output_path), ri=False)
            if log_coords:
                np.savetxt(output_path.with_suffix(".txt"), coords)

    else:
        print(
            f"[italic white]\tEmpty cropped array, skipping for coordinates {coords}..."
        )

    if ri:
        return cropped_image
