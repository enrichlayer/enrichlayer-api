"""
Tests for proxycurl-py compatibility layer.

These tests verify that the monkey patching functionality works correctly
and that existing proxycurl-py code can work with EnrichLayer backend.
"""

import sys
import unittest
from unittest.mock import Mock, patch


class TestProxycurlCompatibility(unittest.TestCase):
    """Test proxycurl compatibility functionality."""

    def setUp(self):
        """Set up test environment."""
        # Clear any existing proxycurl modules from cache
        modules_to_clear = [
            name for name in sys.modules.keys() if name.startswith("proxycurl")
        ]
        for module_name in modules_to_clear:
            del sys.modules[module_name]

    def test_enable_compatibility_function_exists(self):
        """Test that enable_proxycurl_compatibility function is accessible."""
        import enrichlayer_client.compat as enrichlayer
        
        self.assertTrue(hasattr(enrichlayer, "enable_proxycurl_compatibility"))
        self.assertTrue(callable(enrichlayer.enable_proxycurl_compatibility))

    def test_compatibility_wrapper_class_creation(self):
        """Test that wrapper classes are created correctly."""
        from enrichlayer_client.compat.monkey_patch import (
            create_proxycurl_wrapper_class,
        )
        from enrichlayer_client.asyncio import EnrichLayer

        # Create wrapper class
        WrapperClass = create_proxycurl_wrapper_class(EnrichLayer)

        # Verify it's a class and can be instantiated
        self.assertTrue(isinstance(WrapperClass, type))

        # Create mock instance to avoid real API calls
        with patch.object(EnrichLayer, "__init__", return_value=None):
            instance = WrapperClass()
            self.assertTrue(hasattr(instance, "linkedin"))

    def test_linkedin_wrapper_provides_correct_interface(self):
        """Test that LinkedinCompatibilityWrapper provides the right interface."""
        from enrichlayer_client.compat.monkey_patch import LinkedinCompatibilityWrapper

        # Create mock enrichlayer instance
        mock_enrichlayer = Mock()
        mock_enrichlayer.person = Mock()
        mock_enrichlayer.company = Mock()
        mock_enrichlayer.school = Mock()
        mock_enrichlayer.job = Mock()
        mock_enrichlayer.customers = Mock()

        # Create wrapper
        linkedin_wrapper = LinkedinCompatibilityWrapper(mock_enrichlayer)

        # Verify all expected properties exist
        self.assertTrue(hasattr(linkedin_wrapper, "person"))
        self.assertTrue(hasattr(linkedin_wrapper, "company"))
        self.assertTrue(hasattr(linkedin_wrapper, "school"))
        self.assertTrue(hasattr(linkedin_wrapper, "job"))
        self.assertTrue(hasattr(linkedin_wrapper, "customers"))

        # Verify they delegate correctly through ErrorMappingWrapper
        self.assertEqual(linkedin_wrapper.person._wrapped, mock_enrichlayer.person)
        self.assertEqual(linkedin_wrapper.company._wrapped, mock_enrichlayer.company)
        self.assertEqual(linkedin_wrapper.school._wrapped, mock_enrichlayer.school)
        self.assertEqual(linkedin_wrapper.job._wrapped, mock_enrichlayer.job)
        self.assertEqual(linkedin_wrapper.customers._wrapped, mock_enrichlayer.customers)

    def test_environment_variable_handling(self):
        """Test that PROXYCURL_API_KEY is handled correctly."""
        with patch.dict("os.environ", {"PROXYCURL_API_KEY": "test-key"}, clear=True):
            from enrichlayer_client.compat.monkey_patch import (
                create_proxycurl_wrapper_class,
            )
            from enrichlayer_client.asyncio import EnrichLayer

            WrapperClass = create_proxycurl_wrapper_class(EnrichLayer)

            # Mock the parent __init__ to capture the arguments
            with patch.object(EnrichLayer, "__init__", return_value=None) as mock_init:
                WrapperClass()

                # Verify that api_key was passed correctly
                mock_init.assert_called_once()
                call_args = mock_init.call_args
                self.assertEqual(call_args[1]["api_key"], "test-key")

    def test_module_patching(self):
        """Test that module patching works correctly."""
        from enrichlayer_client.compat.monkey_patch import patch_proxycurl_module
        from enrichlayer_client.asyncio import EnrichLayer

        # Create a simple class to act as the mock module
        class MockModule:
            def __init__(self):
                self.Proxycurl = Mock()
                self.__name__ = 'test.module'
                
        mock_module = MockModule()
        mock_original_proxycurl = mock_module.Proxycurl
        
        # Add module to sys.modules for the test
        test_module_name = "test.module"
        sys.modules[test_module_name] = mock_module

        try:
            # Patch the module
            patch_proxycurl_module(test_module_name, EnrichLayer, show_warnings=False)

            # Verify the original class was stored
            self.assertEqual(mock_module._original_Proxycurl, mock_original_proxycurl)

            # Verify the class was replaced
            self.assertNotEqual(mock_module.Proxycurl, mock_original_proxycurl)
        finally:
            # Clean up
            if test_module_name in sys.modules:
                del sys.modules[test_module_name]

    def test_enable_compatibility_with_parameters(self):
        """Test enable_proxycurl_compatibility with parameters."""
        import enrichlayer_client.compat as enrichlayer
        
        with patch.dict("os.environ", {}, clear=True):
            with patch(
                "enrichlayer_client.compat.monkey_patch.patch_proxycurl_module"
            ) as mock_patch:

                # Call with parameters
                enrichlayer.enable_proxycurl_compatibility(
                    api_key="test-key",
                    base_url="https://test.com",
                    deprecation_warnings=True,
                )

                # Verify environment variables were set
                import os

                self.assertEqual(os.environ.get("ENRICHLAYER_API_KEY"), "test-key")
                self.assertEqual(os.environ.get("PROXYCURL_API_KEY"), "test-key")
                self.assertEqual(os.environ.get("BASE_URL"), "https://test.com")

                # Verify patching was called for all modules
                # expected_calls = [
                #     ("proxycurl.asyncio", unittest.mock.ANY, True),
                #     ("proxycurl.gevent", unittest.mock.ANY, True),
                #     ("proxycurl.twisted", unittest.mock.ANY, True),
                # ]

                actual_calls = [call[0] for call in mock_patch.call_args_list]
                self.assertEqual(len(actual_calls), 3)

                # Check module names
                module_names = [call[0] for call in actual_calls]
                self.assertIn("proxycurl.asyncio", module_names)
                self.assertIn("proxycurl.gevent", module_names)
                self.assertIn("proxycurl.twisted", module_names)


if __name__ == "__main__":
    unittest.main()
