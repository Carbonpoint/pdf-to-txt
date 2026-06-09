import argparse
from pathlib import Path

from .extract import convert_pdf_to_txt


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a PDF file to text using native or Nougat OCR extraction."
    )
    parser.add_argument("input", type=str)
    parser.add_argument("output", type=str)
    parser.add_argument(
        "--engine",
        choices=["native", "nougat", "hybrid"],
        default="hybrid",
    )

    args = parser.parse_args()

    convert_pdf_to_txt(
        Path(args.input),
        Path(args.output),
        engine=args.engine,
    )


if __name__ == "__main__":
    main()
