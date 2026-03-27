import unittest
from app.utils.filename_parser import parse_filename
from app.utils.chunking import chunk_text

class TestUtils(unittest.TestCase):
    def test_filename_parser_valid(self):
        filename = "D-2023 - Decreto de prueba.pdf"
        metadata = parse_filename(filename)
        self.assertEqual(metadata.tipo, "Decreto")
        self.assertEqual(metadata.anio, 2023)
        self.assertIn("Decreto de prueba", metadata.title)

    def test_filename_parser_invalid(self):
        filename = "invalid.txt"
        metadata = parse_filename(filename)
        self.assertIsNone(metadata)

    def test_chunking(self):
        text = "ABCDEFGHIJ"
        chunks = chunk_text(text, chunk_size=3, overlap=1)
        # Expected: "ABC", "CDE", "EFG", "GHI", "IJ"
        self.assertGreater(len(chunks), 1)
        self.assertIn("ABC", chunks)

if __name__ == "__main__":
    unittest.main()
