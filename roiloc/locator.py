from pathlib import PosixPath
from typing import Union

import nibabel as nib
import numpy as np


def get_coords(x: np.ndarray, margin: list = [4, 4, 2]) -> list:
    """Get coordinates of a given ROI, and apply a margin.

    Args:
        x (np.ndarray): ROI in binary format
        margin (list, optional): margin for xyz axes. Defaults to [4, 4, 2]

    Returns:
        list: Coordinates in xyzxyz format
    """
    ux, uy, uz = x.shape

    mask = np.where(x != 0)

    minx, maxx = int(np.min(mask[0])), int(np.max(mask[0]))
    miny, maxy = int(np.min(mask[1])), int(np.max(mask[1]))
    minz, maxz = int(np.min(mask[2])), int(np.max(mask[2]))

    minx = (minx - margin[0]) if (minx - margin[0]) > 0 else 0
    miny = (miny - margin[1]) if (miny - margin[1]) > 0 else 0
    minz = (minz - margin[2]) if (minz - margin[2]) > 0 else 0
    maxx = (maxx + margin[0]) if (maxx + margin[0]) < ux else ux
    maxy = (maxy + margin[1]) if (maxy + margin[1]) < uy else uy
    maxz = (maxz + margin[2]) if (maxz + margin[2]) < uz else uz

    return [minx, miny, minz, maxx, maxy, maxz]


def crop(image_path: Union[str, PosixPath], coords: list,
         output_path: Union[str, PosixPath]):
    """Crop an image given some xyzxyz coordinates, and save it.

    Args:
        image_path (Union[str, PosixPath]): Path of the original MRI
        coords (list): xyzxyz coordinates of the ROI
        output_path (Union[str, PosixPath]): Path of the output file
    """
    original_image = nib.load(image_path)

    cropped_array = original_image.get_fdata()[coords[0]:coords[3],
                                               coords[1]:coords[4],
                                               coords[2]:coords[5]]

    cropped = nib.Nifti1Image(cropped_array,
                              affine=original_image.affine,
                              header=original_image.header)

    nib.save(cropped, output_path)
