from pathlib import PosixPath
from typing import Optional

import ants
from ants.core.ants_image import ANTsImage


def register(fixed: ANTsImage,
             moving: ANTsImage,
             type_of_transform: list,
             path: Optional[PosixPath] = None,
             mask: Optional[str] = None) -> dict:
    """Registration wrapper around ANTs

    Args:
        fixed (ANTsImage): Image that stays in the native space
        moving (ANTsImage): Image to move in native space
        type_of_transform (list): See ANTs doc for registration type
        path (Optional[PosixPath], optional): Path where to find masks. Defaults to None.
        mask (Optional[str], optional): Pattern to find masks. Defaults to None.

    Returns:
        dict: Registration results
    """
    if mask:
        mask_path = list(path.glob(mask))
        if mask_path:
            mask = ants.image_read(str(mask_path[0]), pixeltype="unsigned int")
            print(f"Using mask {str(mask_path[0])}")
        else:
            print(
                "[bold red]Warning: no mask found. Registering without mask...")

    return ants.registration(fixed=fixed,
                             moving=moving,
                             type_of_transform=type_of_transform,
                             mask=mask)