import ants
from ants.core.ants_image import ANTsImage

SUPPORTED_CONTRASTS = ["t1", "t2"]


def get_mni(contrast: str, bet: bool) -> ANTsImage:
    """Get the correct MNI ICBM152 09c Asym template,
    given contrast and BET status.

    Args:
        contrast (str): MRI's contrast, t1 or t2
        bet (bool): Bool to indicate the brain extraction status

    Returns:
        ANTsImage: Correct MNI template
    """
    assert contrast in SUPPORTED_CONTRASTS

    betstr = "bet" if bet else ""

    return ants.image_read(
        f"roiloc/MNI/icbm152/mni_icbm152_{contrast}{betstr}_tal_nlin_sym_09c.nii",
        pixeltype="float")


def get_roi(image: ANTsImage,
            atlas: ANTsImage,
            idx: int,
            transform: list,
            output_dir: str,
            output_file: str,
            save: bool = True) -> ANTsImage:
    """Get the registered ROI from CerebrA atlas, into a
    subject's native space.

    Args:
        image (ANTsImage): Subject's MRI
        atlas (ANTsImage): CerebrA Atlas
        idx (int): Index of the ROI
        transform (list): Transformation from MNI to Native space
        output_dir (str): Where to save the ROIs
        output_file (str): Name of the ROIs
        save (bool, optional): Save or not the ROIs. Defaults to True.

    Returns:
        ANTsImage: ROI in native space
    """
    hippocampus = ants.apply_transforms(fixed=image,
                                        moving=atlas,
                                        transformlist=transform,
                                        interpolator="nearestNeighbor")

    hippocampus[hippocampus != idx] = 0

    if save:
        hippocampus.to_file(f"{output_dir}/{output_file}")

    return hippocampus
