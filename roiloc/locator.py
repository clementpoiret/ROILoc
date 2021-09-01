from typing import Optional

import ants
import numpy as np
from ants.core import ANTsImage

from .location import crop, get_coords
from .registration import get_roi
from .template import get_atlas, get_mni, get_roi_indices


class RoiLocator:
    """Crop an MRI image to a ROI.

    Args:
        contrast (str): Contrast to use for registration.
        roi (str): ROI to use for registration.
        bet (bool, optional): Use brain extracted MNI template. Defaults to False.
        transform_type (str, optional): Type of transformation for the registration.
                                        Defaults to "AffineFast".
        margin (list, optional): Margin to apply. Defaults to [4, 4, 4].
        mask (Optional[ANTsImage], optional): Brain mask to improve registration quality.
                                              Defaults to None.

    Attributes:
        coords (dict): Dictionary of coordinates for each side of the ROI.
        _fwdtransforms (list): List of forward transforms.
        _invtransforms (list): List of inverse transforms.
        _mni (ANTsImage): MNI template.
        _atlas (ANTsImage): CerebrA atlas image.
        _roi_idx (list): List of indices for the ROI in the CerebrA atlas.
        _image (ANTsImage): Input image used to inverse transform.

    Exemples:
        >>> from roiloc.locator import RoiLocator
    """

    def __init__(self,
                 contrast: str,
                 roi: str,
                 bet: bool = False,
                 transform_type: str = "AffineFast",
                 margin: list = [4, 4, 4],
                 mask: Optional[ANTsImage] = None):

        self.transform_type = transform_type
        self.margin = margin
        self.mask = mask

        self._roi_idx = get_roi_indices(roi)
        self._mni = get_mni(contrast, bet)
        self._atlas = get_atlas()

        self._image = None
        self._fwdtransforms = None
        self._invtransforms = None
        self.coords = {}

    def get_coords(self) -> dict:
        """Get the coordinates of the ROI.

        Returns:
            dict: Dictionary of coordinates for each side of the ROI.
        """
        return self.coords

    def fit(self, image: ANTsImage):
        """Fit the ROI to the image and set coords.

        Args:
            image (ANTsImage): Image to fit the ROI to.
        """
        self._image = image

        registration = ants.registration(fixed=image,
                                         moving=self._mni,
                                         type_of_transform=self.transform_type,
                                         mask=self.mask)

        self._fwdtransforms = registration["fwdtransforms"]
        self._invtransforms = registration["invtransforms"]

        registered_atlas = ants.apply_transforms(
            fixed=image,
            moving=self._atlas,
            transformlist=self._fwdtransforms,
            interpolator="nearestNeighbor")

        for i, side in enumerate(["right", "left"]):
            region = get_roi(registered_atlas=registered_atlas,
                             idx=int(self._roi_idx[i]),
                             save=False)
            coords = get_coords(region.numpy(), margin=self.margin)

            self.coords[side] = coords

    def transform(self, image: ANTsImage) -> list:
        """Crop the image to the ROI.

        Args:
            image (ANTsImage): Image to transform.

        Returns:
            list: List of transformed images.
        """
        return [
            crop(image, self.coords[side], log_coords=False, ri=True)
            for side in ["right", "left"]
        ]

    def fit_transform(self, image: ANTsImage) -> list:
        """Fit the ROI to the image and transform.

        Args:
            image (ANTsImage): Image to fit the ROI to.

        Returns:
            list: List of transformed images.
        """
        self.fit(image)
        return self.transform(image)

    def inverse_transform(self, image: ANTsImage) -> ANTsImage:
        """Inverse transform the image to the native space.

        Args:
            image (ANTsImage): Image to inverse transform.

        Returns:
            ANTsImage: Inverse transformed image.
        """
        empty_image = self._image.new_image_like(
            np.zeros_like(self._image.numpy()))

        return ants.decrop_image(image, empty_image)


def test():
    image = ants.image_read(
        "~/Datasets/MemoDev/ManualSegmentation/mb190108/tse.nii.gz",
        reorient="LPI")
    locator = RoiLocator(contrast="t2", roi="hippocampus", bet=True)

    right, _ = locator.fit_transform(image)
    print(locator.get_coords())
    right_orig = locator.inverse_transform(right)

    assert right_orig.shape == image.shape
