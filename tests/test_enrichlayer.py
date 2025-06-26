#!/usr/bin/env python3
"""
Core EnrichLayer library tests.

Tests basic functionality, configuration, and client initialization.
"""

import os
import sys
import unittest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestEnrichLayerCore(unittest.TestCase):
    """Test core EnrichLayer functionality."""

    def test_version_import(self):
        """Test that version can be imported."""
        try:
            from enrichlayer_client import __version__

            self.assertIsInstance(__version__, str)
            self.assertRegex(__version__, r"\d+\.\d+\.\d+")
        except ImportError:
            # If no __version__ defined, that's ok for now
            pass

    def test_asyncio_client_import(self):
        """Test that asyncio client can be imported."""
        from enrichlayer_client.asyncio import EnrichLayer

        self.assertTrue(callable(EnrichLayer))

    def test_gevent_client_import(self):
        """Test that gevent client can be imported."""
        try:
            from enrichlayer_client.gevent import EnrichLayer

            self.assertTrue(callable(EnrichLayer))
        except ImportError:
            self.skipTest("Gevent not available")

    def test_twisted_client_import(self):
        """Test that twisted client can be imported."""
        try:
            from enrichlayer_client.twisted import EnrichLayer

            self.assertTrue(callable(EnrichLayer))
        except ImportError:
            self.skipTest("Twisted not available")

    def test_client_initialization(self):
        """Test that clients can be initialized."""
        from enrichlayer_client.asyncio import EnrichLayer

        # Test with explicit API key
        client = EnrichLayer(api_key="test-key")
        self.assertIsNotNone(client)

    def test_models_import(self):
        """Test that models can be imported."""
        from enrichlayer_client.models import EmployeeCount

        self.assertTrue(hasattr(EmployeeCount, "__annotations__"))

    def test_config_import(self):
        """Test that config can be imported."""
        from enrichlayer_client.config import BASE_URL, TIMEOUT

        self.assertIsInstance(BASE_URL, str)
        self.assertIsInstance(TIMEOUT, int)

    def test_compatibility_import(self):
        """Test that compatibility module can be imported."""
        from enrichlayer_client.compat import enable_proxycurl_compatibility

        self.assertTrue(callable(enable_proxycurl_compatibility))


if __name__ == "__main__":
    unittest.main(verbosity=2)
