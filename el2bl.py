#!/usr/bin/env python3
"""el2bl: convert Evernote note links to Bear note links"""
import os
import re
import argparse
import warnings
from bs4 import BeautifulSoup, CData, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

BEAR_LINK_ESCAPE = r"([\\\[\]|/])"


def input_enex_path():
    """Read .enex files in directory.
    ---
    - Accept path to directory from user input
    - Verify that directory is valid with os.path.exists()
    - Scan directory with os.scandir and create files object
    - Create directory for converted files
    - Run function to convert links in each file
    """
    parser = argparse.ArgumentParser(
        description="Cleans Evernote enex files to be Bear compatible"
    )
    parser.add_argument(
        "path", type=str, nargs="?", help="file path to directory of evernote files"
    )
    parser.add_argument(
        "-d",
        dest="debug",
        default=False,
        const=True,
        action="store_const",
        help="Enable more debug output",
    )
    args = parser.parse_args()
    if args.path:
        path = args.path
    else:
        path = input("Please input the path to a directory with Evernote exports: ")
    if not os.path.exists(path):
        print(f"Not a valid file path:\n{path}")
        exit
    elif os.path.isfile(path):
        print(f"Not a valid directory path: {path}")
        exit
    elif not os.listdir(path):
        print(f"Directory is empty: {path}")
        exit
    else:
        print(f"Valid directory path: {path}")

    if not os.path.exists(f"{path}/bear"):
        os.mkdir(f"{path}/bear")
    for file in os.scandir(path):
        if file.is_file() and file.name.endswith(".enex"):
            try:
                convert_links(file)
            except Exception as e:
                if args.debug:
                    raise
                print(f"An error occured:\n{e}\nPlease try again.")


def convert_links(file):
    """Convert links in .enex files to Bear note link format.
    ---
    - Read contents of file with Beautiful Soup, and convert to string
    - Replace Evernote note link URIs, but not other URIs, with Bear note links
    - Remove H1 tags from note body
    - Write to a new file in the bear subdirectory
    """
    print(f"Converting {file.name}...")
    with open(file, "r") as enex:
        soup = BeautifulSoup(enex, "html.parser")
        for note in soup.find_all("note"):
            sub_soup = BeautifulSoup(note.content.string, "html.parser")
            for link in sub_soup.find_all("a", href=re.compile("evernote://")):
                link.string = re.sub(BEAR_LINK_ESCAPE, r"\\\1", link.string)
                link.insert_before("[[")
                link.insert_after("]]")
                link.unwrap()
            # for heading in soup.find_all('h1'):
            # heading.name = 'strong'
            note.content.string = CData(str(sub_soup))
        with open(f"{os.path.dirname(file)}/bear/{file.name}", "w") as new_enex:
            new_enex.write(str(soup))
        print("Done. New file available in the bear subdirectory.")


if __name__ == "__main__":
    input_enex_path()
