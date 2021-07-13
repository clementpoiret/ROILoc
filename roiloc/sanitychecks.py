from typing import Union

import ants
import nibabel as nib
from ants.core.ants_image import ANTsImage
from nibabel.nifti1 import Nifti1Image
from nibabel.nifti2 import Nifti2Image


def is_lpi_ants(image: ANTsImage) -> bool:
    """Check if the ants image is LPI-

    Args:
        image (ANTsImage): MRI

    Returns:
        bool: LPI- status
    """
    return ants.get_orientation(image) == "LPI"


def is_ras_nib(image: Union[Nifti1Image, Nifti2Image]) -> bool:
    """Check if the ants image is RAS+

    Args:
        image (Union[Nifti1Image, Nifti2Image]): MRI

    Returns:
        bool: RAS+ status
    """
    return "".join(nib.aff2axcodes(image.affine)) == "RAS"
