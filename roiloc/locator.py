from typing import Optional

import ants
from ants.core import ANTsImage

from .location import crop, get_coords
from .registration import get_roi, register
from .template import get_atlas, get_mni, get_roi_indices


class RoiLocator:

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
        return self.coords

    def fit(self, image: ANTsImage):
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
        return [
            crop(image, self.coords[side], log_coords=False, ri=True)
            for side in ["right", "left"]
        ]

    def fit_transform(self, image: ANTsImage) -> list:
        self.fit(image)
        return self.transform(image)

    def inverse_transform(self, image: ANTsImage) -> ANTsImage:
        return ants.decrop_image(image, self._image)


def test():
    image = ants.image_read(
        "~/Datasets/MemoDev/ManualSegmentation/mb190108/tse.nii.gz",
        reorient="LPI")
    locator = RoiLocator(contrast="t2", roi="hippocampus", bet=True)

    right, _ = locator.fit_transform(image)
    print(locator.get_coords())
    right_orig = locator.inverse_transform(right)

    assert right_orig.shape == image.shape
