"""
Script to center and crop an MRI based on regions given by the CerebrA atlas.
Distributed under MIT License by Clément POIRET.
"""

import argparse
from pathlib import Path

import ants
import importlib_resources
from rich import print
from rich.console import Console
from rich.progress import track

from roiloc.location import crop, get_coords
from roiloc.registration import get_roi, register
from roiloc.template import get_mni, get_roi_indices

console = Console()


def main(args):
    print(
        "For information purposes, you are currently running ROILoc with the following config:"
    )
    console.log(args)

    path = Path(args.path).expanduser()

    # Getting roi from cerebra's csv
    rois_idx = {roi: get_roi_indices(roi) for roi in args.roi}
    # roi_idx = get_roi_indices(args.roi)

    # Loading mris, template and atlas
    images = list(path.glob(args.inputpattern))
    if not images:
        print(
            "[bold red]Warning: no image found. Please double check your path and pattern."
        )

    mni = get_mni(args.contrast, args.bet)
    res = importlib_resources.files("roiloc")
    data = str(res / "MNI" / "cerebra" /
               "mni_icbm152_CerebrA_tal_nlin_sym_09c.nii")
    atlas = ants.image_read(data, pixeltype="unsigned int")

    for image_path in track(images):
        stem = image_path.stem.split(".")[0]

        print(f"\n[bold blue]Processing {str(image_path)}")
        image = ants.image_read(str(image_path), pixeltype="float")

        print("Registering MNI to native space...")
        registration = register(image,
                                mni,
                                args.transform,
                                path=image_path.parent,
                                mask=args.mask)

        registered_atlas = ants.apply_transforms(
            fixed=image,
            moving=atlas,
            transformlist=registration["fwdtransforms"],
            interpolator="nearestNeighbor")

        for roi in rois_idx:
            print(f"Transforming and saving {roi}...")

            for i, side in enumerate(["right", "left"]):
                region = get_roi(
                    registered_atlas=registered_atlas,
                    idx=int(rois_idx[roi][i]),
                    output_dir=str(image_path.parent),
                    output_file=
                    f"{stem}_{roi}_{side}_{args.transform}_mask.nii.gz",
                    save=True)

                coords = get_coords(region.numpy(), margin=args.margin)

                crop(
                    image_path, coords, image_path.parent /
                    f"{stem}_{roi}_{side}_{args.transform}_crop.nii.gz")

    print("[bold green]Done! :)")


def start():
    parser = argparse.ArgumentParser(
        description=
        "Locate the Hippocampus or any other CerebrA ROI by using MNI152 Template and CerebrA Atlas"
    )

    parser.add_argument("-p",
                        "--path",
                        help="<Required> Input images path.",
                        required=True,
                        type=str)

    parser.add_argument(
        "-i",
        "--inputpattern",
        help=
        "<Required> Pattern to find input images in input path (e.g.: `**/*t1*.nii.gz`).",
        required=True,
        type=str)

    parser.add_argument(
        "-r",
        "--roi",
        nargs='+',
        help=
        "ROI included in CerebrA. See `roiloc/MNI/cerebra/CerebrA_LabelDetails.csv` for more details. Default: 'Hippocampus'.",
        required=False,
        default=["Hippocampus"],
        type=str)

    parser.add_argument(
        "-c",
        "--contrast",
        help="<Required> Contrast of the input MRI. Can be `t1` or `t2`.",
        required=True,
        type=str)

    parser.add_argument(
        "-b",
        "--bet",
        help=
        "Boolean to choose if we use the BET version of the MNI152 template.",
        required=False,
        default=False,
        type=bool)

    parser.add_argument(
        "-t",
        "--transform",
        help=
        "Type of registration. See `https://antspy.readthedocs.io/en/latest/registration.html` for the complete list of options. Default: `AffineFast`",
        required=False,
        default="AffineFast",
        type=str)

    parser.add_argument(
        "-m",
        "--margin",
        nargs='+',
        type=int,
        help=
        "Margin to add around the bounding box in voxels. It has to be a list of 3 integers, to control the margin in the three axis. Default: [8,8,2]",
        required=False,
        default=[8, 8, 2])

    parser.add_argument(
        "--mask",
        help=
        "Pattern for brain tissue mask to improve registration (e.g.: `**/sub_*bet_mask.nii.gz`). If providing a BET mask, please also pass `-b True` to use a BET MNI template.",
        required=False,
        type=str,
        default=None)

    args = parser.parse_args()

    print("""[bold green]Copyright (C) 2021  Clément POIRET[/bold green]
    This program comes with [bold magenta]ABSOLUTELY NO WARRANTY[/bold magenta]; for help, launch it with `-h`.
    This is free software, and you are welcome to redistribute it under certain conditions.\n\n"""
         )

    main(args)
