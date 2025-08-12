import sys
import os
import time
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from fastapi.testclient import TestClient
import main


class StaticFilesTest(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(main.app)

    def test_static_files(self):
        response = self.client.get("/static/")
        time.sleep(3)
        self.assertEqual(response.status_code, 200)
        self.assertIn("index.html", response.text)


if __name__ == "__main__":
    unittest.main()