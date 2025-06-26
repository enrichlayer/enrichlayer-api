"""
EnrichLayer API - Python client for LinkedIn data enrichment.

This package provides a modern, efficient Python client for accessing
LinkedIn profile and company data through the EnrichLayer API.

Basic usage:
    from enrichlayer_client.asyncio import EnrichLayer

    enrichlayer = EnrichLayer()
    person = await enrichlayer.person.get(linkedin_profile_url="...")

Proxycurl compatibility:
    For users migrating from proxycurl-py, import the compatibility module directly:

    from enrichlayer_client.compat import enable_proxycurl_compatibility
    enable_proxycurl_compatibility()

    # Now your existing proxycurl code works unchanged
    from proxycurl.asyncio import Proxycurl
    proxycurl = Proxycurl()
    person = await proxycurl.linkedin.person.get(...)
"""

__version__ = "0.1.0.post2"
