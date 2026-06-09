from __future__ import annotations

from pathlib import Path
from typing import Iterator
import sys
import json
import re

# Optional libraries
try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

try:
    import pdfplumber  # type: ignore
except Exception:
    pdfplumber = None

try:
    import pytesseract
except (ImportError, Exception):
    pytesseract = None

try:
    import cv2
except Exception:
    cv2 = None

try:
    import numpy as np
except Exception:
    np = None

try:
    from PIL import Image
except Exception:
    Image = None

from PyPDF2 import PdfReader
from PyPDF2.errors import FileNotDecryptedError

DEFAULT_SOURCE_DIR = Path(r"C:\Users\silverframe\Zotero\storage")
DEFAULT_OUTPUT_DIR = Path(r"C:\Users\silverframe\Projects\zotero-text-server\txt")


# -------------------------
# Text cleanup helpers
# -------------------------

def _merge_hyphenation(text: str) -> str:
    return re.sub(r"(\w)-\n(\w)", r"\1\2", text)


def _normalize_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# -------------------------
# OCR
# -------------------------

def _ocr_image(img: Image.Image) -> str:
    if pytesseract is None:
        return ""

    try:
        if cv2 is not None and np is not None:
            arr = np.array(img)
            gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
            _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            processed = Image.fromarray(th)
        else:
            processed = img

        text = pytesseract.image_to_string(processed)
        return _normalize_whitespace(text)

    except Exception:
        try:
            return pytesseract.image_to_string(img)
        except Exception:
            return ""


# -------------------------
# Core text extraction
# -------------------------

def extract_text_with_structure(pdf_path: Path) -> tuple[str, dict]:
    metadata = {"pages": 0, "used_ocr": False, "figures": 0}

    # --- pdfplumber (preferred)
    if pdfplumber is not None:
        try:
            with pdfplumber.open(str(pdf_path)) as doc:
                metadata["pages"] = len(doc.pages)
                texts = []

                for page in doc.pages:
                    txt = page.extract_text() or ""
                    txt = _merge_hyphenation(txt)
                    txt = _normalize_whitespace(txt)

                    # OCR ONLY if text is missing
                    if not txt.strip() and pytesseract and Image:
                        metadata["used_ocr"] = True
                        try:
                            img = page.to_image(resolution=150).original
                            ocr_text = _ocr_image(img)
                            if ocr_text:
                                txt = ocr_text
                        except Exception:
                            pass

                    texts.append(txt)

                return "\n\n".join(filter(None, texts)), metadata

        except Exception:
            pass

    # --- PyMuPDF fallback
    if fitz is not None:
        try:
            doc = fitz.open(str(pdf_path))
            metadata["pages"] = doc.page_count
            texts = []

            for pno in range(doc.page_count):
                page = doc.load_page(pno)
                txt = page.get_text("text") or ""
                txt = _merge_hyphenation(txt)
                txt = _normalize_whitespace(txt)

                if not txt.strip() and pytesseract and Image:
                    metadata["used_ocr"] = True
                    try:
                        pix = page.get_pixmap(dpi=150)
                        img = Image.frombytes(
                            "RGB",
                            [pix.width, pix.height],
                            pix.samples,
                        )
                        ocr_text = _ocr_image(img)
                        if ocr_text:
                            txt = ocr_text
                    except Exception:
                        pass

                texts.append(txt)

            return "\n\n".join(filter(None, texts)), metadata

        except Exception:
            pass

    # --- Final fallback: PyPDF2
    try:
        reader = PdfReader(pdf_path)
    except Exception as exc:
        print(f"Warning: skipping {pdf_path}: {exc}", file=sys.stderr)
        return "", metadata

    try:
        texts = []
        for page in reader.pages:
            txt = page.extract_text() or ""
            txt = _merge_hyphenation(txt)
            txt = _normalize_whitespace(txt)
            texts.append(txt)
        return "\n\n".join(filter(None, texts)), metadata
    except (FileNotDecryptedError, Exception) as exc:
        # Skip encrypted or unreadable files
        print(f"Warning: skipping {pdf_path} (encrypted or unreadable): {exc}", file=sys.stderr)
        return "", metadata


# -------------------------
# Figure extraction
# -------------------------

def extract_figures(pdf_path: Path, figures_dir: Path) -> int:
    figures_dir.mkdir(parents=True, exist_ok=True)
    count = 0

    if fitz is None or Image is None:
        return 0

    try:
        doc = fitz.open(str(pdf_path))

        for pno in range(doc.page_count):
            page = doc.load_page(pno)
            images = page.get_images(full=True)

            for img in images:
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)

                if pix.n > 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)

                img_pil = Image.frombytes(
                    "RGB",
                    [pix.width, pix.height],
                    pix.samples,
                )

                count += 1
                out_path = figures_dir / f"fig_{count:03d}.png"
                img_pil.save(out_path)

        return count

    except Exception:
        return 0


# -------------------------
# File utilities
# -------------------------

def iter_pdf_files(source_dir: Path) -> Iterator[Path]:
    return (p for p in source_dir.rglob("*.pdf") if p.is_file())


def build_txt_path(pdf_path: Path, source_dir: Path, output_dir: Path) -> Path:
    return output_dir.joinpath(pdf_path.relative_to(source_dir)).with_suffix(".txt")


def _save_json_metadata(txt_path: Path, metadata: dict) -> None:
    try:
        txt_path.with_suffix(".json").write_text(
            json.dumps(metadata, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass


# -------------------------
# Conversion
# -------------------------

def convert_pdf_to_txt(pdf_path: Path, txt_path: Path) -> None:
    txt_path.parent.mkdir(parents=True, exist_ok=True)

    text, metadata = extract_text_with_structure(pdf_path)

    figures_dir = txt_path.parent / f"{txt_path.stem}.figures"
    figures = extract_figures(pdf_path, figures_dir)
    metadata["figures"] = figures

    # Append figure references
    if figures > 0:
        refs = "\n".join(f"[FIGURE: fig_{i:03d}.png]" for i in range(1, figures + 1))
        text = (text + "\n\n" + refs).strip() if text else refs

    try:
        txt_path.write_text(text, encoding="utf-8")
    except Exception as e:
        print(f"Warning: failed writing {txt_path}: {e}", file=sys.stderr)

    _save_json_metadata(txt_path, metadata)


def convert_pdf_directory(source_dir: Path, output_dir: Path, refresh: bool = False) -> int:
    source_dir = source_dir.resolve()
    output_dir = output_dir.resolve()

    output_dir.mkdir(parents=True, exist_ok=True)

    pdfs = list(iter_pdf_files(source_dir))
    if not pdfs:
        print("No PDFs found.")
        return 0

    if not refresh:
        pdfs = [p for p in pdfs if not build_txt_path(p, source_dir, output_dir).exists()]

    converted = 0

    for i, pdf in enumerate(pdfs, 1):
        print(f"[{i}/{len(pdfs)}] Converting {pdf.name}", end="\r")
        txt_path = build_txt_path(pdf, source_dir, output_dir)
        convert_pdf_to_txt(pdf, txt_path)
        converted += 1

    print()
    print(f"Converted {converted} PDFs.")
    return converted