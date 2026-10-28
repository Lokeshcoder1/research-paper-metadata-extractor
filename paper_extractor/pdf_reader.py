from dataclasses import dataclass
from pathlib import Path

import pymupdf


class PDFExtractionError(RuntimeError):
    """Raised when a PDF cannot be read or processed."""


@dataclass(frozen=True)
class PDFTextDocument:
    """Raw text extracted from a PDF document."""

    source_path: Path
    page_texts: tuple[str, ...]

    @property
    def page_count(self) -> int:
        return len(self.page_texts)

    @property
    def text(self) -> str:
        """Combine pages while preserving page boundaries."""
        return "\n\f\n".join(self.page_texts)

    @property
    def character_count(self) -> int:
        """Count extracted characters, excluding surrounding whitespace."""
        return sum(len(page.strip()) for page in self.page_texts)

    @property
    def pages_without_text(self) -> tuple[int, ...]:
        """Return one-based page numbers containing no extracted text."""
        return tuple(
            page_number
            for page_number, page_text in enumerate(
                self.page_texts, start=1
            )
            if not page_text.strip()
        )

    @property
    def likely_needs_ocr(self) -> bool:
        """
        Flag documents with very little extracted text.

        This is only a heuristic, not proof that a PDF is scanned.
        """
        return self.character_count < 100


def extract_pdf_text(pdf_path: str | Path) -> PDFTextDocument:
    """Extract raw text from every page of a PDF."""

    path = Path(pdf_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    if not path.is_file():
        raise ValueError(f"Expected a file, received: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file: {path}")

    try:
        with pymupdf.open(str(path)) as document:
            if document.needs_pass and not document.authenticate(""):
                raise PDFExtractionError(
                    f"PDF is password-protected: {path.name}"
                )

            page_texts = []

            for page_number, page in enumerate(document, start=1):
                try:
                    page_text = page.get_text("text", sort=True)
                    page_texts.append(page_text or "")
                except Exception as exc:
                    raise PDFExtractionError(
                        f"Failed to extract page {page_number} "
                        f"from {path.name}"
                    ) from exc

            if not page_texts:
                raise PDFExtractionError(
                    f"PDF contains no pages: {path.name}"
                )

    except PDFExtractionError:
        raise
    except Exception as exc:
        raise PDFExtractionError(
            f"Could not read PDF {path.name}: {exc}"
        ) from exc

    return PDFTextDocument(
        source_path=path,
        page_texts=tuple(page_texts),
    )