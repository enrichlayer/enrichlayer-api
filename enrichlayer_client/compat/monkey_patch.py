"""
Monkey patching utilities for proxycurl-py compatibility.

This module provides the core functionality to patch the existing proxycurl-py
package to use EnrichLayer backend instead of the original Proxycurl backend.
"""

from __future__ import annotations

import asyncio
import functools
import os
import sys
from typing import Any, Optional
import warnings

# Supported concurrency variants
VARIANTS = ["asyncio", "gevent", "twisted"]

# Module-level mappings populated at import time
AVAILABLE_PROXYCURL_VARIANTS = {}
AVAILABLE_ENRICHLAYER_VARIANTS = {}
EXCEPTION_CLASS_MAPPING = {}


def _initialize_variants():
    """Initialize all variant mappings once at module import time"""
    for variant in VARIANTS:
        # Check proxycurl variant availability
        try:
            proxycurl_module = __import__(
                f"proxycurl.{variant}.base", fromlist=["ProxycurlException"]
            )
            AVAILABLE_PROXYCURL_VARIANTS[variant] = proxycurl_module.ProxycurlException
        except ImportError:
            pass

        # Check enrichlayer variant availability
        try:
            enrichlayer_module = __import__(
                f"enrichlayer_client.{variant}", fromlist=["EnrichLayer"]
            )
            AVAILABLE_ENRICHLAYER_VARIANTS[variant] = enrichlayer_module.EnrichLayer
        except ImportError:
            pass

        # Build exception mapping for available variants
        if variant in AVAILABLE_PROXYCURL_VARIANTS:
            EXCEPTION_CLASS_MAPPING[
                f"enrichlayer_client.{variant}"
            ] = AVAILABLE_PROXYCURL_VARIANTS[variant]


def _verify_proxycurl_available():
    """Verify that proxycurl-py is installed with at least one variant available"""
    if not AVAILABLE_PROXYCURL_VARIANTS:
        raise ImportError(
            "The compatibility module requires proxycurl-py to be installed. "
            "Install it with: pip install proxycurl-py"
        ) from None
    return list(AVAILABLE_PROXYCURL_VARIANTS.keys())


# Initialize variants and verify proxycurl-py availability at module import
_initialize_variants()
_verify_proxycurl_available()


def error_mapping_decorator(func: Any) -> Any:
    """
    Decorator that catches EnrichLayerException and re-raises as ProxycurlException.

    This ensures that users of the compatibility layer see proxycurl-style errors
    instead of enrichlayer-specific errors.

    Uses module-level EXCEPTION_CLASS_MAPPING for consistent, static mapping.
    """

    def get_proxycurl_exception(exception: Exception):
        """Get the appropriate ProxycurlException class for the given enrichlayer exception"""
        module = getattr(exception.__class__, "__module__", "")

        # Find matching mapping by checking if module contains the key
        for (
            enrichlayer_module,
            proxycurl_exception_class,
        ) in EXCEPTION_CLASS_MAPPING.items():
            if enrichlayer_module in module:
                return proxycurl_exception_class

        # No mapping found - raise original exception
        raise exception

    def is_enrichlayer_exception(exception: Exception) -> bool:
        """Check if the exception is an EnrichLayerException using actual class comparison"""
        # Get all available EnrichLayerException classes from initialized variants
        enrichlayer_exceptions = []

        for variant in AVAILABLE_ENRICHLAYER_VARIANTS:
            try:
                enrichlayer_module = __import__(
                    f"enrichlayer_client.{variant}.base",
                    fromlist=["EnrichLayerException"],
                )
                enrichlayer_exceptions.append(enrichlayer_module.EnrichLayerException)
            except (ImportError, AttributeError):
                pass

        # Check if exception is instance of any EnrichLayerException
        return any(
            isinstance(exception, exc_class) for exc_class in enrichlayer_exceptions
        )

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if is_enrichlayer_exception(e):
                # Get the appropriate ProxycurlException class based on the enrichlayer variant
                ProxycurlExceptionClass = get_proxycurl_exception(e)
                # Re-raise as ProxycurlException with the same message and context
                raise ProxycurlExceptionClass(str(e)) from e
            else:
                # Re-raise other exceptions unchanged
                raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if is_enrichlayer_exception(e):
                # Get the appropriate ProxycurlException class based on the enrichlayer variant
                ProxycurlExceptionClass = get_proxycurl_exception(e)
                # Re-raise as ProxycurlException with the same message and context
                raise ProxycurlExceptionClass(str(e)) from e
            else:
                # Re-raise other exceptions unchanged
                raise

    # Return appropriate wrapper based on whether the function is async
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


class ErrorMappingWrapper:
    """
    Wrapper that applies error mapping to all methods of an object.

    This ensures that all method calls from the wrapped object get proper
    error mapping from EnrichLayerException to ProxycurlException.
    """

    def __init__(self, wrapped_object: Any) -> None:
        self._wrapped = wrapped_object

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._wrapped, name)
        if callable(attr):
            return error_mapping_decorator(attr)
        return attr


class LinkedinCompatibilityWrapper:
    """
    Wrapper that provides the linkedin.* interface for compatibility.

    Maps the old proxycurl.linkedin.* structure to the new enrichlayer direct access.
    """

    def __init__(self, enrichlayer_instance: Any) -> None:
        self._enrichlayer = enrichlayer_instance

    @property
    def person(self) -> Any:
        """Provides access to person methods via enrichlayer.person with error mapping"""
        return ErrorMappingWrapper(self._enrichlayer.person)

    @property
    def company(self) -> Any:
        """Provides access to company methods via enrichlayer.company with error mapping"""
        return ErrorMappingWrapper(self._enrichlayer.company)

    @property
    def school(self) -> Any:
        """Provides access to school methods via enrichlayer.school with error mapping"""
        return ErrorMappingWrapper(self._enrichlayer.school)

    @property
    def job(self) -> Any:
        """Provides access to job methods via enrichlayer.job with error mapping"""
        return ErrorMappingWrapper(self._enrichlayer.job)

    @property
    def customers(self) -> Any:
        """Provides access to customers methods via enrichlayer.customers with error mapping"""
        return ErrorMappingWrapper(self._enrichlayer.customers)


def create_proxycurl_wrapper_class(enrichlayer_class: type[Any]) -> type[Any]:
    """
    Creates a Proxycurl wrapper class that uses EnrichLayer backend.

    Args:
        enrichlayer_class: The EnrichLayer class to wrap (AsyncIO, Gevent, or Twisted)

    Returns:
        A class that mimics the original Proxycurl interface
    """

    class ProxycurlCompatibilityWrapper(enrichlayer_class):
        """
        Proxycurl compatibility wrapper that delegates to EnrichLayer.

        This class maintains the exact same interface as the original Proxycurl
        class but uses EnrichLayer backend for all operations.
        """

        def __init__(
            self,
            api_key: Optional[str] = None,
            base_url: Optional[str] = None,
            timeout: Optional[int] = None,
            max_retries: Optional[int] = None,
            max_backoff_seconds: Optional[int] = None,
            **kwargs: Any,
        ) -> None:
            # Handle legacy PROXYCURL_API_KEY environment variable
            if api_key is None:
                api_key = os.environ.get("PROXYCURL_API_KEY") or os.environ.get(
                    "ENRICHLAYER_API_KEY", ""
                )

            # Initialize the EnrichLayer backend with only non-None values
            init_kwargs: dict[str, Any] = {"api_key": api_key}
            if base_url is not None:
                init_kwargs["base_url"] = base_url
            if timeout is not None:
                init_kwargs["timeout"] = timeout
            if max_retries is not None:
                init_kwargs["max_retries"] = max_retries
            if max_backoff_seconds is not None:
                init_kwargs["max_backoff_seconds"] = max_backoff_seconds
            init_kwargs.update(kwargs)

            super().__init__(**init_kwargs)

            # Store reference for method delegation
            self.enrichlayer = self

            # Create the linkedin compatibility wrapper
            self.linkedin = LinkedinCompatibilityWrapper(self)

        @error_mapping_decorator
        def get_balance(self, **kwargs: Any) -> Any:
            """Maintain compatibility for get_balance method with error mapping"""
            return super().get_balance(**kwargs)

    return ProxycurlCompatibilityWrapper


def _patch_all_variants(show_warnings: bool = False) -> None:
    """Patch all available enrichlayer variants"""
    for variant, enrichlayer_class in AVAILABLE_ENRICHLAYER_VARIANTS.items():
        patch_proxycurl_module(f"proxycurl.{variant}", enrichlayer_class, show_warnings)


def patch_proxycurl_module(
    module_name: str, enrichlayer_class: type[Any], show_warnings: bool = False
) -> None:
    """
    Patch a specific proxycurl module to use EnrichLayer backend.

    Args:
        module_name: Name of the module to patch (e.g., 'proxycurl.asyncio')
        enrichlayer_class: The EnrichLayer class to use as backend
        show_warnings: Whether to show deprecation warnings
    """

    if module_name not in sys.modules:
        # Module not imported yet, nothing to patch
        return

    module = sys.modules[module_name]

    if not hasattr(module, "Proxycurl"):
        # Module doesn't have Proxycurl class, nothing to patch
        return

    # Store original class for reference
    if not hasattr(module, "_original_Proxycurl"):
        module._original_Proxycurl = module.Proxycurl  # type: ignore

    # Replace with compatibility wrapper
    module.Proxycurl = create_proxycurl_wrapper_class(enrichlayer_class)  # type: ignore

    if show_warnings:
        warnings.warn(
            f"Module {module_name} has been patched to use EnrichLayer backend. "
            "Consider migrating to enrichlayer-api for future-proof code.",
            FutureWarning,
            stacklevel=3,
        )


def enable_proxycurl_compatibility(
    deprecation_warnings: bool = False,
) -> None:
    """
    Enable proxycurl-py compatibility by monkey patching existing proxycurl modules.

    This function patches the proxycurl-py package (if installed and imported) to use
    the EnrichLayer backend instead of the original Proxycurl backend. This allows
    existing code using proxycurl-py to work unchanged while benefiting from the
    new EnrichLayer infrastructure.

    Args:
        deprecation_warnings: Whether to show warnings about deprecated proxycurl usage

    Example:
        import enrichlayer_client.compat as enrichlayer
        enrichlayer.enable_proxycurl_compatibility()

        # Now existing proxycurl code works with EnrichLayer backend
        from proxycurl.asyncio import Proxycurl
        proxycurl = Proxycurl(api_key="your-key")
        person = proxycurl.linkedin.person.get(linkedin_profile_url="...")

    Note:
        This function should be called before importing any proxycurl modules.
        API keys should be passed to the Proxycurl constructor as normal.
    """

    # Patch all available enrichlayer variants
    _patch_all_variants(deprecation_warnings)

    # Set up import hooks for future imports
    _setup_import_hooks(deprecation_warnings)


def _setup_import_hooks(show_warnings: bool = False) -> None:
    """
    Set up import hooks to automatically patch proxycurl modules when they're imported.

    This ensures that even if proxycurl modules are imported after calling
    enable_proxycurl_compatibility(), they will still be patched.
    """

    # Store original __import__ to call later
    original_import = (
        __builtins__["__import__"]
        if isinstance(__builtins__, dict)
        else __builtins__.__import__
    )

    def patching_import(name, globals=None, locals=None, fromlist=(), level=0):
        """Custom import function that patches proxycurl modules after they're imported."""

        # Call the original import first
        module = original_import(name, globals, locals, fromlist, level)

        # Check if we imported a proxycurl module that needs patching
        if name.startswith("proxycurl."):
            variant = name.split(".")[
                -1
            ]  # Extract variant name (asyncio/gevent/twisted)
            if variant in AVAILABLE_ENRICHLAYER_VARIANTS:
                patch_proxycurl_module(
                    name, AVAILABLE_ENRICHLAYER_VARIANTS[variant], show_warnings
                )

        return module

    # Replace the built-in __import__ function
    if isinstance(__builtins__, dict):
        __builtins__["__import__"] = patching_import
    else:
        __builtins__.__import__ = patching_import


def disable_proxycurl_compatibility():
    """
    Disable proxycurl compatibility and restore original Proxycurl classes.

    This function restores the original Proxycurl classes in all loaded
    proxycurl modules, effectively disabling the EnrichLayer backend.
    """

    modules_to_restore = ["proxycurl.asyncio", "proxycurl.gevent", "proxycurl.twisted"]

    for module_name in modules_to_restore:
        if module_name in sys.modules:
            module = sys.modules[module_name]
            if hasattr(module, "_original_Proxycurl"):
                module.Proxycurl = module._original_Proxycurl
                delattr(module, "_original_Proxycurl")

    # Remove import hooks
    sys.meta_path = [
        hook
        for hook in sys.meta_path
        if not (
            hasattr(hook, "__class__")
            and getattr(hook.__class__, "__name__", "") == "ProxycurlImportHook"
        )
    ]
