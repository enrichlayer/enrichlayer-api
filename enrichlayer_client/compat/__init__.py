"""
Compatibility module for proxycurl-py integration.

This module provides monkey patching capabilities to make existing
proxycurl-py code work with the new enrichlayer-api backend.
"""

from .monkey_patch import enable_proxycurl_compatibility

__all__ = ["enable_proxycurl_compatibility"]
