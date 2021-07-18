import ants
from ants.core.ants_image import ANTsImage


def is_lpi(image: ANTsImage) -> bool:
    """Check if the ants image is LPI-

    Args:
        image (ANTsImage): MRI

    Returns:
        bool: LPI- status
    """
    return ants.get_orientation(image) == "LPI"
