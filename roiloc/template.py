import ants
import importlib_resources
import pandas as pd
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

    template = f"mni_icbm152_{contrast}{betstr}_tal_nlin_sym_09c.nii"
    res = importlib_resources.files("roiloc")
    data = str(res / "MNI" / "icbm152" / template)
    return ants.image_read(str(data), pixeltype="float")


def get_roi_indices(roi: str) -> list:
    roi = roi.title()

    res = importlib_resources.files("roiloc")
    data = str(res / "MNI" / "cerebra" / "CerebrA_LabelDetails.csv")
    cerebra = pd.read_csv(data, index_col="Label Name")

    return [cerebra.loc[roi, "RH Label"], cerebra.loc[roi, "LH Labels"]]
