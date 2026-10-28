import tempfile
import unittest
from pathlib import Path

import pymupdf

from paper_extractor.pdf_reader import (
    PDFExtractionError,
    extract_pdf_text,
)


class TestPDFReader(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_pdf(self, filename, page_texts):
        path = self.temp_path / filename
        document = pymupdf.open()

        for text in page_texts:
            page = document.new_page()

            if text:
                page.insert_text((72, 72), text)

        document.save(str(path))
        document.close()

        return path

    def test_extracts_text_from_multiple_pages(self):
        path = self.create_pdf(
            "sample.pdf",
            [
                "Research Paper Title",
                "Benchmark: Accuracy 85%",
            ],
        )

        result = extract_pdf_text(path)

        self.assertEqual(result.page_count, 2)
        self.assertIn("Research Paper Title", result.page_texts[0])
        self.assertIn("Accuracy 85%", result.page_texts[1])
        self.assertIn("\f", result.text)

    def test_missing_file_raises_error(self):
        missing_path = self.temp_path / "missing.pdf"

        with self.assertRaises(FileNotFoundError):
            extract_pdf_text(missing_path)

    def test_non_pdf_file_is_rejected(self):
        text_file = self.temp_path / "sample.txt"
        text_file.write_text("Not a PDF", encoding="utf-8")

        with self.assertRaises(ValueError):
            extract_pdf_text(text_file)

    def test_invalid_pdf_raises_error(self):
        invalid_pdf = self.temp_path / "invalid.pdf"
        invalid_pdf.write_text("Not a real PDF", encoding="utf-8")

        with self.assertRaises(PDFExtractionError):
            extract_pdf_text(invalid_pdf)

    def test_empty_text_triggers_ocr_warning(self):
        path = self.create_pdf("empty.pdf", [""])

        result = extract_pdf_text(path)

        self.assertTrue(result.likely_needs_ocr)
        self.assertEqual(result.pages_without_text, (1,))


if __name__ == "__main__":
    unittest.main()