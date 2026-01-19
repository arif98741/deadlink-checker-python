import sys
import os
import unittest

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from deadlink.utils import is_external_url, normalize_url
from deadlink.version import VERSION

class TestCore(unittest.TestCase):
    def test_version_exists(self):
        self.assertIsNotNone(VERSION)
        print(f"Testing version: {VERSION}")

    def test_url_normalization(self):
        url = "https://example.com/path/"
        normalized = normalize_url(url)
        self.assertEqual(normalized, "https://example.com/path")

    def test_external_link_check(self):
        base = "https://example.com"
        external = "https://google.com"
        internal = "https://example.com/about"
        
        self.assertTrue(is_external_url(external, base))
        self.assertFalse(is_external_url(internal, base))

if __name__ == '__main__':
    unittest.main()
