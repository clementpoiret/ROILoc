"""
Script to center and crop an MRI based on regions given by the CerebrA atlas.
Distributed under MIT License by Clément POIRET.
"""

import argparse
from pathlib import Path

import ants
import pandas as pd
from rich import print
from rich.console import Console
from rich.progress import track

from roiloc.locator import crop, get_coords
from roiloc.template import get_mni, get_roi

console = Console()


def main(args):
    print(
        "For information purposes, you are currently running ROILoc with the following config:"
    )
    console.log(args)

    path = Path(args.path).expanduser()

    # Getting roi from cerebra's csv
    roi = args.roi.title()
    cerebra = pd.read_csv("roiloc/MNI/cerebra/CerebrA_LabelDetails.csv",
                          index_col="Label Name")
    roi_idx = [cerebra.loc[roi, "RH Label"], cerebra.loc[roi, "LH Labels"]]

    # Loading mris, template and atlas
    images = list(path.glob(args.inputpattern))

    if not images:
        print(
            "[bold red]Warning: no image found. Please double check your path and pattern."
        )

    mni = get_mni(args.contrast, args.bet)
    atlas = ants.image_read(
        "./roiloc/MNI/cerebra/mni_icbm152_CerebrA_tal_nlin_sym_09c.nii",
        pixeltype="unsigned int")

    for image_path in track(images):
        stem = image_path.stem.split(".")[0]

        print(f"\n[bold blue]Processing {str(image_path)}")

        image = ants.image_read(str(image_path), pixeltype="float")

        print("Registering MNI to native space...")

        mask = None
        if args.mask:
            mask_path = list(image_path.parent.glob(args.mask))
            if mask_path:
                mask = ants.image_read(str(mask_path[0]),
                                       pixeltype="unsigned int")
                print(f"Using mask {str(mask_path[0])}")
            else:
                print(
                    "[bold red]Warning: no mask found. Registering without mask..."
                )

        registration = ants.registration(fixed=image,
                                         moving=mni,
                                         type_of_transform=args.transform,
                                         mask=mask)

        print("Transforming and saving rois...")
        for i, side in enumerate(["right", "left"]):
            region = get_roi(
                image=image,
                atlas=atlas,
                idx=int(roi_idx[i]),
                transform=registration["fwdtransforms"],
                output_dir=str(image_path.parent),
                output_file=
                f"{stem}_{args.roi}_{side}_{args.transform}_mask.nii.gz",
                save=True)

            coords = get_coords(region.numpy(), margin=args.margin)

            crop(
                image_path, coords, image_path.parent /
                f"{stem}_{args.roi}_{side}_{args.transform}_crop.nii.gz")

    print("[bold green]Done! :)")


if __name__ == "__main__":
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
        help=
        "ROI included in CerebrA. See `roiloc/MNI/cerebra/CerebrA_LabelDetails.csv` for more details. Default: 'Hippocampus'.",
        required=False,
        default="Hippocampus",
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
