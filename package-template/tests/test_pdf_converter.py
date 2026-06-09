from pathlib import Path

import pytest
from PyPDF2 import PdfWriter

from my_package.pdf_converter import convert_pdf_directory


def create_blank_pdf(path: Path) -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with path.open("wb") as handle:
        writer.write(handle)


def test_convert_pdf_directory_reports_zero_for_empty_source(tmp_path: Path) -> None:
    source = tmp_path / "source"
    output = tmp_path / "output"
    source.mkdir()

    converted = convert_pdf_directory(source, output)

    assert converted == 0
    assert output.exists()
    assert list(output.rglob("*")) == []


def test_convert_pdf_directory_raises_for_same_or_nested_output(tmp_path: Path) -> None:
    source = tmp_path / "source"
    output_same = source
    output_nested = source / "nested"
    source.mkdir(parents=True)
    output_nested.mkdir(parents=True)

    with pytest.raises(ValueError):
        convert_pdf_directory(source, output_same)

    with pytest.raises(ValueError):
        convert_pdf_directory(source, output_nested)


def test_convert_pdf_directory_skips_existing_txt(tmp_path: Path) -> None:
    source = tmp_path / "source"
    output = tmp_path / "output"
    source.mkdir()
    output.mkdir()

    pdf_file = source / "sample.pdf"
    create_blank_pdf(pdf_file)
    existing_txt = output / "sample.txt"
    existing_txt.write_text("already converted", encoding="utf-8")

    converted = convert_pdf_directory(source, output)

    assert converted == 0
    assert existing_txt.read_text(encoding="utf-8") == "already converted"


def test_convert_pdf_directory_refresh_overwrites_existing_output(tmp_path: Path) -> None:
    source = tmp_path / "source"
    output = tmp_path / "output"
    source.mkdir()
    output.mkdir()

    pdf_file = source / "sample.pdf"
    create_blank_pdf(pdf_file)
    existing_txt = output / "sample.txt"
    existing_txt.write_text("old text", encoding="utf-8")

    converted = convert_pdf_directory(source, output, refresh=True)

    assert converted == 1
    assert existing_txt.exists()
    assert existing_txt.read_text(encoding="utf-8") != "old text"
