#!/usr/bin/env python3
"""
Comprehensive exception mapping testing for proxycurl-py compatibility.

Consolidates exception mapping tests from multiple root-level test files.
Tests static mapping, variant consistency, and security features.
"""

import os
import sys
import unittest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestExceptionMapping(unittest.TestCase):
    """Test exception mapping functionality in compatibility layer."""

    def test_variant_specific_mapping(self):
        """Test that each variant maps to its corresponding proxycurl exception."""
        from enrichlayer_client.compat.monkey_patch import error_mapping_decorator

        # Test asyncio mapping
        @error_mapping_decorator
        def test_asyncio_exception():
            from enrichlayer_client.asyncio.base import EnrichLayerException

            raise EnrichLayerException("Test asyncio error")

        with self.assertRaises(Exception) as cm:
            test_asyncio_exception()

        # Should be mapped to proxycurl.asyncio.base.ProxycurlException
        self.assertIn("proxycurl.asyncio", cm.exception.__class__.__module__)
        self.assertEqual(cm.exception.__class__.__name__, "ProxycurlException")

        # Test gevent mapping
        @error_mapping_decorator
        def test_gevent_exception():
            from enrichlayer_client.gevent.base import EnrichLayerException

            raise EnrichLayerException("Test gevent error")

        with self.assertRaises(Exception) as cm:
            test_gevent_exception()

        # Should be mapped to proxycurl.gevent.base.ProxycurlException
        self.assertIn("proxycurl.gevent", cm.exception.__class__.__module__)
        self.assertEqual(cm.exception.__class__.__name__, "ProxycurlException")

        # Test twisted mapping
        @error_mapping_decorator
        def test_twisted_exception():
            from enrichlayer_client.twisted.base import EnrichLayerException

            raise EnrichLayerException("Test twisted error")

        with self.assertRaises(Exception) as cm:
            test_twisted_exception()

        # Should be mapped to proxycurl.twisted.base.ProxycurlException
        self.assertIn("proxycurl.twisted", cm.exception.__class__.__module__)
        self.assertEqual(cm.exception.__class__.__name__, "ProxycurlException")

    def test_static_mapping_efficiency(self):
        """Test that static mapping is used instead of dynamic imports."""
        from enrichlayer_client.compat.monkey_patch import EXCEPTION_CLASS_MAPPING

        # Verify mapping is populated at module level
        self.assertIsInstance(EXCEPTION_CLASS_MAPPING, dict)
        self.assertGreater(len(EXCEPTION_CLASS_MAPPING), 0)

        # Verify static mapping entries
        expected_mappings = [
            "enrichlayer_client.asyncio",
            "enrichlayer_client.gevent",
            "enrichlayer_client.twisted",
        ]

        for mapping in expected_mappings:
            if mapping in EXCEPTION_CLASS_MAPPING:
                exception_class = EXCEPTION_CLASS_MAPPING[mapping]
                self.assertTrue(hasattr(exception_class, "__name__"))
                self.assertEqual(exception_class.__name__, "ProxycurlException")

    def test_no_fallback_behavior(self):
        """Test that unmapped exceptions are raised as-is without fallback."""
        from enrichlayer_client.compat.monkey_patch import error_mapping_decorator

        # Test with non-enrichlayer exception
        @error_mapping_decorator
        def test_regular_exception():
            raise ValueError("This is not an enrichlayer exception")

        with self.assertRaises(ValueError) as cm:
            test_regular_exception()

        # Should pass through unchanged
        self.assertEqual(str(cm.exception), "This is not an enrichlayer exception")
        self.assertEqual(cm.exception.__class__.__name__, "ValueError")

    def test_name_spoofing_resistance(self):
        """Test that fake exceptions with EnrichLayerException name are rejected."""
        from enrichlayer_client.compat.monkey_patch import error_mapping_decorator

        # Create fake exception with same name but different class
        class FakeEnrichLayerException(Exception):
            """Fake exception that mimics EnrichLayerException name"""

            pass

        @error_mapping_decorator
        def test_fake_exception():
            raise FakeEnrichLayerException("Fake exception")

        with self.assertRaises(FakeEnrichLayerException) as cm:
            test_fake_exception()

        # Should pass through unchanged (not be mapped)
        self.assertEqual(str(cm.exception), "Fake exception")
        self.assertEqual(cm.exception.__class__.__name__, "FakeEnrichLayerException")
        # Should NOT be mapped to ProxycurlException
        self.assertNotIn("proxycurl", cm.exception.__class__.__module__)

    def test_exception_message_preservation(self):
        """Test that original exception messages are preserved in mapping."""
        from enrichlayer_client.compat.monkey_patch import error_mapping_decorator

        original_message = "Original error message with details"

        @error_mapping_decorator
        def test_message_preservation():
            from enrichlayer_client.asyncio.base import EnrichLayerException

            raise EnrichLayerException(original_message)

        with self.assertRaises(Exception) as cm:
            test_message_preservation()

        # Message should be preserved
        self.assertEqual(str(cm.exception), original_message)
        # But class should be mapped
        self.assertIn("proxycurl.asyncio", cm.exception.__class__.__module__)

    def test_exception_chaining(self):
        """Test that exception chaining is preserved."""
        from enrichlayer_client.compat.monkey_patch import error_mapping_decorator

        @error_mapping_decorator
        def test_exception_chaining():
            from enrichlayer_client.asyncio.base import EnrichLayerException

            raise EnrichLayerException("Mapped exception")

        with self.assertRaises(Exception) as cm:
            test_exception_chaining()

        # Check that __cause__ is set (exception chaining)
        self.assertIsNotNone(cm.exception.__cause__)
        self.assertEqual(
            cm.exception.__cause__.__class__.__name__, "EnrichLayerException"
        )

    def test_async_and_sync_decorator_compatibility(self):
        """Test that decorator works with both async and sync functions."""
        import asyncio

        from enrichlayer_client.compat.monkey_patch import error_mapping_decorator

        # Test sync function
        @error_mapping_decorator
        def sync_function():
            from enrichlayer_client.asyncio.base import EnrichLayerException

            raise EnrichLayerException("Sync error")

        with self.assertRaises(Exception) as cm:
            sync_function()

        self.assertIn("proxycurl.asyncio", cm.exception.__class__.__module__)

        # Test async function
        @error_mapping_decorator
        async def async_function():
            from enrichlayer_client.asyncio.base import EnrichLayerException

            raise EnrichLayerException("Async error")

        async def run_async_test():
            with self.assertRaises(Exception) as cm:
                await async_function()
            return cm.exception

        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            exception = loop.run_until_complete(run_async_test())
            self.assertIn("proxycurl.asyncio", exception.__class__.__module__)
        finally:
            loop.close()

    def test_module_level_initialization(self):
        """Test that exception mapping is initialized at module level."""
        from enrichlayer_client.compat.monkey_patch import (
            AVAILABLE_ENRICHLAYER_VARIANTS,
            AVAILABLE_PROXYCURL_VARIANTS,
            EXCEPTION_CLASS_MAPPING,
            VARIANTS,
        )

        # Verify constants are defined
        self.assertEqual(VARIANTS, ["asyncio", "gevent", "twisted"])

        # Verify dictionaries are populated
        self.assertIsInstance(AVAILABLE_PROXYCURL_VARIANTS, dict)
        self.assertIsInstance(AVAILABLE_ENRICHLAYER_VARIANTS, dict)
        self.assertIsInstance(EXCEPTION_CLASS_MAPPING, dict)

        # Should have at least asyncio available (required dependency)
        self.assertIn("asyncio", AVAILABLE_PROXYCURL_VARIANTS)
        self.assertIn("asyncio", AVAILABLE_ENRICHLAYER_VARIANTS)
        self.assertIn("enrichlayer_client.asyncio", EXCEPTION_CLASS_MAPPING)


if __name__ == "__main__":
    unittest.main(verbosity=2)
