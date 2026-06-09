import argparse
from pathlib import Path

try:
    from .pdf_converter import (
        DEFAULT_OUTPUT_DIR,
        DEFAULT_SOURCE_DIR,
        convert_pdf_directory,
    )
except ImportError:  # pragma: no cover - allows direct script execution
    from pdf_converter import (
        DEFAULT_OUTPUT_DIR,
        DEFAULT_SOURCE_DIR,
        convert_pdf_directory,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert PDF files in a source directory into text files in a cloned destination directory."
    )
    parser.add_argument(
        "--source",
        default=str(DEFAULT_SOURCE_DIR),
        help=f"Source directory containing PDF files (default: {DEFAULT_SOURCE_DIR})",
    )
    parser.add_argument(
        "--destination",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Destination root directory for text output (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Regenerate all text files instead of only converting missing outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_dir = Path(args.source)
    destination_dir = Path(args.destination)
    converted = convert_pdf_directory(
        source_dir,
        destination_dir,
        refresh=args.refresh,
    )
    print(f"Converted {converted} PDF file(s) to text.")


if __name__ == "__main__":
    main()
