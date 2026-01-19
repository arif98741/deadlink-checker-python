import sys
import os
import unittest
import tempfile
import shutil

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from deadlink.utils import is_external_url, normalize_url, get_status_text
from deadlink.models import LinkResult
from deadlink.reporter import generate_report, get_report_filename
from deadlink.database import DatabaseManager
from deadlink.scanner import get_all_links
from deadlink.version import VERSION
from unittest.mock import patch, MagicMock

class TestCore(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_version_exists(self):
        self.assertIsNotNone(VERSION)
        print(f"Testing version: {VERSION}")

    def test_url_normalization(self):
        url = "https://example.com/path/"
        normalized = normalize_url(url)
        # normalize_url should strip trailing slash for paths
        self.assertEqual(normalized, "https://example.com/path")
        
        url_with_query = "https://example.com/path/?q=1#frag"
        normalized_q = normalize_url(url_with_query)
        self.assertEqual(normalized_q, "https://example.com/path?q=1")
        
        url_home = "https://example.com/"
        # home page should keep trailing slash
        self.assertEqual(normalize_url(url_home), "https://example.com/")

    def test_external_link_check(self):
        base = "https://example.com"
        external = "https://google.com"
        internal = "https://example.com/about"
        internal_www = "https://www.example.com/about"
        
        self.assertTrue(is_external_url(external, base))
        self.assertFalse(is_external_url(internal, base))
        self.assertFalse(is_external_url(internal_www, base))

    def test_status_text_lookup(self):
        self.assertEqual(get_status_text(200), "200 OK")
        self.assertEqual(get_status_text(404), "404 Not Found")
        self.assertEqual(get_status_text(500), "500 Internal Server Error")
        self.assertIn("999", get_status_text(999))

    def test_link_result_model(self):
        res = LinkResult(
            url="https://test.com",
            status_code=200,
            status_text="OK",
            response_time=0.5,
            found_on="https://base.com",
            is_dead=False,
            is_external=True,
            link_type="Image"
        )
        self.assertEqual(res.url, "https://test.com")
        self.assertTrue(res.is_external)
        self.assertFalse(res.is_dead)
        self.assertEqual(res.link_type, "Image")

    def test_report_generation(self):
        results = [
            LinkResult("https://a.com", 200, "OK", 0.1, "base", False, False),
            LinkResult("https://b.com", 404, "Not Found", 0.1, "base", True, False),
            LinkResult("https://external.com", 200, "OK", 0.1, "base", False, True)
        ]
        report = generate_report(results)
        self.assertIn("DEAD LINK CHECKER REPORT", report)
        self.assertIn("Total items checked: 3", report)
        self.assertIn("Working items:    2", report)
        self.assertIn("Dead items:       1", report)
        self.assertIn("Internal:   2", report)
        self.assertIn("External:   1", report)

    def test_report_filename_generation(self):
        url = "https://www.Example-Site.com/page"
        filename = get_report_filename(url, "csv", reports_dir=self.test_dir)
        self.assertIn("example-site_com", filename)
        self.assertTrue(filename.endswith(".csv"))
        
        filename_session = get_report_filename(url, "txt", reports_dir=self.test_dir, session_folder="session_1")
        self.assertIn("session_1", filename_session)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "session_1")))

    def test_database_manager(self):
        # Use in-memory database for testing
        db = DatabaseManager(":memory:")
        results = [
            LinkResult("https://a.com", 200, "OK", 0.1, "base", False, False)
        ]
        session_id = db.save_session("https://test.com", "website", results, "folder_1")
        
        sessions = db.get_sessions()
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]['url'], "https://test.com")
        
        session_results = db.get_session_results(session_id)
        self.assertEqual(len(session_results), 1)
        self.assertEqual(session_results[0]['url'], "https://a.com")
        
        db.delete_session(session_id)
        self.assertEqual(len(db.get_sessions()), 0)

    @patch('requests.get')
    def test_link_scraper(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<html><body><a href="/page1">Link</a><img src="img.png"></body></html>'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        links, base = get_all_links("https://test.com")
        self.assertEqual(len(links), 2)
        urls = [l[0] for l in links]
        self.assertIn("https://test.com/page1", urls)
        self.assertIn("https://test.com/img.png", urls)

if __name__ == '__main__':
    unittest.main()
