#!/usr/bin/env python3
import os
import re

from argparse import ArgumentParser, ArgumentTypeError


def valid_dir(path: str) -> str:
    if not os.path.isdir(path):
        raise ArgumentTypeError(f"Path {path} is not a valid directory")
    return path


def parse_enex(file: str) -> str:
    """
    Open the file as read only and return a cleaned string
    """
    with open(file, "r") as enex:
        soup = enex.read()

        soup_sub = re.sub(
            r'(<a[^>]*href="evernote[^>]*?>)(.*?)(</a>)',
            lambda x: "[[{}]]".format(x.group(2).replace("/", "\\/")),
            soup,
        )

        soup_sub = re.sub(
            r'(<span style="color:rgb[^>]*?>)(.*?)(</span>)', r"==\2==", soup_sub
        )

    return soup_sub


def main() -> None:
    # Parse all the arguments
    parser = ArgumentParser(
        description="Clean Evernote enex files to be Bear compatible"
    )
    parser.add_argument("enex_dir", type=valid_dir, help="Path to enex directory")
    parser.add_argument(
        "-o",
        "--output_dir",
        type=valid_dir,
        help="Path to the output directory for clean files",
    )
    args = parser.parse_args()

    if not args.output_dir:
        args.output_dir = os.path.join(args.enex_dir, "bear")

    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)

    print(f"Input Directory:  {args.enex_dir}")
    print(f"Output Directory: {args.output_dir}\n")

    # Create a list of .enex files in the enex_dir
    fileList = [
        file
        for file in os.scandir(args.enex_dir)
        if file.is_file() and os.path.splitext(file.path)[-1] == ".enex"
    ]

    # print([ f.name for f in fileList ])

    for file in fileList:
        print(f"({fileList.index(file)+1:3d}/{len(fileList):3d})  {file.name}")
        try:
            with open(os.path.join(args.output_dir, file.name), "x") as f:
                f.write(parse_enex(file))
        except Exception as exc:
            print(f" !!! An error occured: {exc}")

    print("Done.")


if __name__ == "__main__":
    main()
