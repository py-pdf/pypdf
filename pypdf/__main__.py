"""Entry point for the pypdf CLI program."""

import sys
from argparse import ArgumentParser, Namespace
from os.path import basename
from traceback import print_exc
from typing import List, Set

from . import PdfReader, PdfWriter, __version__


def main(argv: List[str] = sys.argv[1:]) -> None:
    """Main CLI entry point"""
    args = parse_args(argv)
    args.func(args)


def cat_cmd(args: Namespace) -> None:
    """Implementation of the cat subcommand"""
    writer = PdfWriter()
    for pdf_filepath in args.pdf_filepaths[:-1]:
        writer.append_pages_from_reader(PdfReader(pdf_filepath))
    writer.write(args.pdf_filepaths[-1])


def extract_images_cmd(args: Namespace) -> None:
    """Implementation of the extract-images subcommand"""
    reader = PdfReader(args.pdf_filepath)
    for page in reader.pages:
        # We use PageObject private methods because the .images iterator
        # does not allow catching errors triggered by _get_image():
        for image_id in page._get_ids_image():
            try:
                image = page._get_image(image_id)
            except Exception:
                # Example of error caugh there: PIL.UnidentifiedImageError
                print_exc()
                continue
            with open(image.name, "wb") as fp:
                fp.write(image.data)
            print(f"Image extracted to {image.name}")  # noqa: T201


def subset_cmd(args: Namespace) -> None:
    """Implementation of the subset subcommand"""
    reader = PdfReader(args.pdf_filepath)
    writer = PdfWriter()
    for i, page in enumerate(reader.pages, start=1):
        if i in args.page_numbers:
            writer.add_page(page)
    if len(writer.pages) != len(args.page_numbers):
        print(  # noqa: T201
            "WARN: Some target pages were not extracted, source PDF has too few pages"
        )
    writer.write(args.out_filepath)


def version_cmd(_: Namespace) -> None:
    """Implementation of --version"""
    print(__version__)  # noqa: T201


def parse_args(argv: List[str]) -> Namespace:
    """Parse CLI arguments, validate them and return an argparse.Namespace object"""
    parser = ArgumentParser(
        prog="pypdf",
        description="Command-line program of the pypdf Python library",
        allow_abbrev=False,
    )
    parser.add_argument(
        "--version", action="store_const", dest="func", const=version_cmd
    )
    subparsers = parser.add_subparsers()
    cat_parser = subparsers.add_parser("cat", help="Concatenate the given PDF files")
    cat_parser.set_defaults(func=cat_cmd)
    cat_parser.add_argument(
        "pdf_filepaths",
        nargs="+",
        help="The last PDF document of the list is the destination",
    )
    extract_images_parser = subparsers.add_parser(
        "extract-images", help="Extract all images from the given PDF file"
    )
    extract_images_parser.set_defaults(func=extract_images_cmd)
    extract_images_parser.add_argument("pdf_filepath")
    subset_parser = subparsers.add_parser(
        "subset", help="Extract pages from the given PDF file"
    )
    subset_parser.set_defaults(func=subset_cmd)
    subset_parser.add_argument("pdf_filepath")
    subset_parser.add_argument(
        "page_ranges",
        nargs="+",
        help="Single page numbers or page ranges in the form N-M",
    )
    subset_parser.add_argument(
        "--out-filepath", help="Default to ./subset.{original-filepath}"
    )
    args = parser.parse_args(argv)
    if args.func == cat_cmd and len(args.pdf_filepaths) < 2:
        parser.error("At least two PDF documents must be provided to the cat command")
    if args.func == subset_cmd:
        if not args.out_filepath:
            # Setting default value:
            args.out_filepath = (
                f"./subset.{basename(args.pdf_filepath)}"  # noqa: PTH119
            )
        args.page_numbers = page_ranges_to_page_numbers(parser, args.page_ranges)
    return args


def page_ranges_to_page_numbers(
    parser: ArgumentParser, page_ranges: List[str]
) -> Set[int]:
    """
    Transform: ["3", "5-7", "9"]
    into: {3, 5, 6, 7, 9}.
    Call parser.error() in case of invalid input.
    """
    page_numbers = set()
    for page_range in page_ranges:
        if "-" in page_range:
            try:
                start, end = map(int, page_range.split("-"))
            except ValueError as error:
                parser.error(f"Invalid page range: {error}")
            page_numbers.update(range(start, end + 1))
        else:
            try:
                page_numbers.add(int(page_range))
            except ValueError as error:
                parser.error(f"Invalid page number: {error}")
    return page_numbers


if __name__ == "__main__":
    main()
