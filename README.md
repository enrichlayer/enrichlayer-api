# `enrichlayer-api` - The official Python client for Enrich Layer API to enrich professional profiles

[![PyPI version](https://badge.fury.io/py/enrichlayer-api.svg)](https://pypi.org/project/enrichlayer-api/)
[![Python Support](https://img.shields.io/pypi/pyversions/enrichlayer-api.svg)](https://pypi.org/project/enrichlayer-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

* [What is Enrich Layer?](#what-is-enrich-layer)
* [Before you install](#before-you-install)
* [Installation and supported Python versions](#installation-and-supported-python-versions)
* [Initializing `enrichlayer-api` with an API Key](#initializing-enrichlayer-api-with-an-api-key)
* [Usage with examples](#usage-with-examples)
  + [Enrich a Person Profile](#enrich-a-person-profile)
  + [Enrich a Company Profile](#enrich-a-company-profile)
  + [Lookup a person](#lookup-a-person)
  + [Lookup a company](#lookup-a-company)
  + [Lookup a Profile URL from a work email address](#lookup-a-profile-url-from-a-work-email-address)
  + [Enrich professional profiles in bulk (from a CSV)](#enrich-professional-profiles-in-bulk-from-a-csv)
  + [More *asyncio* examples](#more-asyncio-examples)
* [Rate limit and error handling](#rate-limit-and-error-handling)
* [API Endpoints and their corresponding documentation](#api-endpoints-and-their-corresponding-documentation)
* [Proxycurl-py Compatibility](#proxycurl-py-compatibility)

## What is Enrich Layer?

**Enrich Layer** is an enrichment API to fetch fresh data on people and businesses. We are a fully-managed API that sits between your application and raw data so that you can focus on building the application; instead of worrying about building a web-scraping team and processing data at scale.

With Enrich Layer, you can programmatically:

- Enrich profiles on people and companies
- Lookup people and companies
- Lookup contact information on people and companies
- Check if an email address is of a disposable nature
- [And more..](https://enrichlayer.com/docs)

Visit [Enrich Layer's website](https://enrichlayer.com) for more details.

## Before you install

You should understand that `enrichlayer-api` was designed with concurrency as a first class citizen from ground-up. To install `enrichlayer-api`, *you have to pick a concurrency model*.

We support the following concurrency models:

* [asyncio](https://docs.python.org/3/library/asyncio.html) - See implementation example [here](examples/lib-asyncio.py).
* [gevent](https://www.gevent.org/) - See implementation example [here](examples/lib-gevent.py).
* [twisted](https://twisted.org/) - See implementation example [here](examples/lib-twisted.py).

The right way to use Enrich Layer API is to make API calls concurrently. In fact, making API requests concurrently is the only way to achieve a high rate of throughput. On the default rate limit, you can enrich up to 432,000 profiles per day. See [this blog post](https://enrichlayer.com/blog/how-to-maximize-throughput) for context.

## Installation and supported Python versions

`enrichlayer-api` is [available on PyPi](https://pypi.org/project/enrichlayer-api/). For which you can install into your project with the following command:

```bash
# install enrichlayer-api with asyncio
$ pip install 'enrichlayer-api[asyncio]'

# install enrichlayer-api with gevent
$ pip install 'enrichlayer-api[gevent]'

# install enrichlayer-api with twisted
$ pip install 'enrichlayer-api[twisted]'
```

`enrichlayer-api` is tested on Python `3.8`, `3.9`, `3.10`, `3.11`, and `3.12`.

## Initializing `enrichlayer-api` with an API Key

You can get an API key by [registering an account](https://enrichlayer.com/auth/register) with Enrich Layer. The API Key can be retrieved from the dashboard.

To use Enrich Layer with the API Key:

* You can run your script with the `ENRICHLAYER_API_KEY` environment variable set.
* Or, you can pass the API key directly when initializing the client.

## Usage with examples

I will be using `enrichlayer-api` with the *asyncio* concurrency model to illustrate some examples on what you can do with Enrich Layer and how the code will look with this library.

For examples with other concurrency models such as:

* *gevent*, see `examples/lib-gevent.py`.
* *twisted*, see `examples/lib-twisted.py`.

### Enrich a Person Profile

Given a *Professional Profile URL*, you can get the entire profile back in structured data with Enrich Layer's [Person Profile API Endpoint](https://enrichlayer.com/docs#people-api-person-profile-endpoint).

```python
from enrichlayer_client.asyncio import EnrichLayer, do_bulk
import asyncio

enrichlayer = EnrichLayer(api_key='your-api-key')
person = asyncio.run(enrichlayer.person.get(
    linkedin_profile_url='https://www.linkedin.com/in/williamhgates/'
))
print('Person Result:', person)
```

### Enrich a Company Profile

Given a *Company Profile URL*, enrich the URL with it's full profile with Enrich Layer's [Company Profile API Endpoint](https://enrichlayer.com/docs#company-api-company-profile-endpoint).

```python
company = asyncio.run(enrichlayer.company.get(
    url='https://www.linkedin.com/company/tesla/'
))
print('Company Result:', company)
```

### Lookup a person

Given a first name and a company name or domain, lookup a person with Enrich Layer's [Person Lookup API Endpoint](https://enrichlayer.com/docs#people-api-person-lookup-endpoint).

```python
lookup_results = asyncio.run(enrichlayer.person.resolve(
    first_name="bill", 
    last_name="gates", 
    company_domain="microsoft.com"
))
print('Person Lookup Result:', lookup_results)
```

### Lookup a company

Given a company name or a domain, lookup a company with Enrich Layer's [Company Lookup API Endpoint](https://enrichlayer.com/docs#company-api-company-lookup-endpoint).

```python
company_lookup_results = asyncio.run(enrichlayer.company.resolve(
    company_name="microsoft", 
    company_domain="microsoft.com"
))
print('Company Lookup Result:', company_lookup_results)
```

### Lookup a Profile URL from a work email address

Given a work email address, lookup a Profile URL with Enrich Layer's [Reverse Work Email Lookup Endpoint](https://enrichlayer.com/docs#contact-api-reverse-work-email-lookup-endpoint).

```python
lookup_results = asyncio.run(enrichlayer.person.resolve_by_email(
    email="anthony.tan@grab.com",
    lookup_depth="deep"
))
print('Reverse Work Email Lookup Result:', lookup_results)
```

### Enrich professional profiles in bulk (from a CSV)

Given a CSV file with a list of professional profile URLs, you can enrich the list in the following manner:

```python
# PROCESS BULK WITH CSV
import csv

bulk_person_data = []
with open('sample.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader, None)
    for row in reader:
        bulk_person_data.append(
            (enrichlayer.person.get, {'linkedin_profile_url': row[0]})
        )
results = asyncio.run(do_bulk(bulk_person_data))

print('Bulk:', results)
```

### More *asyncio* examples

More *asyncio* examples can be found at `examples/lib-asyncio.py`

## Rate limit and error handling

There is no need for you to handle rate limits (`429` HTTP status error). The library handles rate limits automatically with exponential backoff.

However, there is a need for you to handle other error codes. Errors will be returned in the form of `EnrichLayerException`. The [list of possible errors](https://enrichlayer.com/docs#overview-errors) is listed in our API documentation.

## API Endpoints and their corresponding documentation

Here we list the available API endpoints and their corresponding library functions. Do refer to each endpoint's relevant API documentation to find out the required arguments that needs to be fed into the function.

### General
| Function | Endpoint | Credits |
| -------- | -------- | ------- |
| `get_balance()` | [View Credit Balance Endpoint](https://enrichlayer.com/docs#meta-api-view-credit-balance-endpoint) | 0 |

### Person API
| Function | Endpoint | Credits |
| -------- | -------- | ------- |
| `person.get(**kwargs)` | [Person Profile Endpoint](https://enrichlayer.com/docs#people-api-person-profile-endpoint) | 1 |
| `person.search(**kwargs)` | [Person Search Endpoint](https://enrichlayer.com/docs#people-api-person-search-endpoint) | 10 |
| `person.resolve(**kwargs)` | [Person Lookup Endpoint](https://enrichlayer.com/docs#people-api-person-lookup-endpoint) | 2 |
| `person.resolve_by_email(**kwargs)` | [Reverse Work Email Lookup Endpoint](https://enrichlayer.com/docs#contact-api-reverse-work-email-lookup-endpoint) | 1 |
| `person.resolve_by_phone(**kwargs)` | [Reverse Phone Lookup Endpoint](https://enrichlayer.com/docs#contact-api-reverse-phone-lookup-endpoint) | 1 |
| `person.lookup_email(**kwargs)` | [Work Email Lookup Endpoint](https://enrichlayer.com/docs#contact-api-work-email-lookup-endpoint) | 1 |
| `person.personal_contact(**kwargs)` | [Personal Contact Number Lookup Endpoint](https://enrichlayer.com/docs#contact-api-personal-contact-number-lookup-endpoint) | 1 |
| `person.personal_email(**kwargs)` | [Personal Email Lookup Endpoint](https://enrichlayer.com/docs#contact-api-personal-email-lookup-endpoint) | 1 |
| `person.profile_picture(**kwargs)` | [Profile Picture Endpoint](https://enrichlayer.com/docs#people-api-profile-picture-endpoint) | 0 |

### Company API
| Function | Endpoint | Credits |
| -------- | -------- | ------- |
| `company.get(**kwargs)` | [Company Profile Endpoint](https://enrichlayer.com/docs#company-api-company-profile-endpoint) | 1 |
| `company.search(**kwargs)` | [Company Search Endpoint](https://enrichlayer.com/docs#company-api-company-search-endpoint) | 10 |
| `company.resolve(**kwargs)` | [Company Lookup Endpoint](https://enrichlayer.com/docs#company-api-company-lookup-endpoint) | 2 |
| `company.find_job(**kwargs)` | [Job Listings Endpoint](https://enrichlayer.com/docs#jobs-api-jobs-listing-endpoint) | 2 |
| `company.job_count(**kwargs)` | [Job Count Endpoint](https://enrichlayer.com/docs#jobs-api-job-count-endpoint) | 1 |
| `company.employee_count(**kwargs)` | [Employee Count Endpoint](https://enrichlayer.com/docs#company-api-employee-count-endpoint) | 1 |
| `company.employee_list(**kwargs)` | [Employee Listing Endpoint](https://enrichlayer.com/docs#company-api-employee-listing-endpoint) | 1 |
| `company.employee_search(**kwargs)` | [Employee Search Endpoint](https://enrichlayer.com/docs#company-api-employee-search-endpoint) | 3 |
| `company.role_lookup(**kwargs)` | [Role Lookup Endpoint](https://enrichlayer.com/docs#people-api-role-lookup-endpoint) | 3 |
| `company.profile_picture(**kwargs)` | [Company Profile Picture Endpoint](https://enrichlayer.com/docs#company-api-profile-picture-endpoint) | 0 |

### School API
| Function | Endpoint | Credits |
| -------- | -------- | ------- |
| `school.get(**kwargs)` | [School Profile Endpoint](https://enrichlayer.com/docs#school-api-school-profile-endpoint) | 1 |
| `school.student_list(**kwargs)` | [Student Listing Endpoint](https://enrichlayer.com/docs#school-api-student-listing-endpoint) | 1 |

### Job API
| Function | Endpoint | Credits |
| -------- | -------- | ------- |
| `job.get(**kwargs)` | [Job Profile Endpoint](https://enrichlayer.com/docs#jobs-api-job-profile-endpoint) | 1 |

### Customer API
| Function | Endpoint | Credits |
| -------- | -------- | ------- |
| `customers.listing(**kwargs)` | [Customer Listing Endpoint](https://enrichlayer.com/docs#customers-api-listing-endpoint) | 1 |

## Proxycurl-py Compatibility

For users migrating from `proxycurl-py`, `enrichlayer-api` provides a compatibility layer that allows existing code to work unchanged while using the new EnrichLayer backend.

### Prerequisites

Both packages must be installed:

```bash
pip install enrichlayer-api
pip install proxycurl-py
```

### Usage

Enable compatibility mode in your existing code by adding one import line:

```python
from enrichlayer_client.compat import enable_proxycurl_compatibility
enable_proxycurl_compatibility()

# Now your existing proxycurl-py code works unchanged
from proxycurl.asyncio import Proxycurl, do_bulk
proxycurl = Proxycurl(api_key='your-enrichlayer-api-key')

# All existing methods work exactly the same
person = asyncio.run(proxycurl.linkedin.person.get(
    linkedin_profile_url='https://www.linkedin.com/in/williamhgates/'
))
company = asyncio.run(proxycurl.linkedin.company.get(
    url='https://www.linkedin.com/company/apple'
))
```

### Configuration Options

```python
# Enable with deprecation warnings
enable_proxycurl_compatibility(deprecation_warnings=True)

# Then use proxycurl as normal, passing API key to constructor
from proxycurl.gevent import Proxycurl
client = Proxycurl(api_key='your-enrichlayer-api-key')
```

### Migration Path

1. **Immediate**: Add compatibility import to existing code
2. **Gradual**: Replace imports one by one:
   ```python
   # Old: from proxycurl.asyncio import Proxycurl
   # New: from enrichlayer_client.asyncio import EnrichLayer as Proxycurl
   ```
3. **Complete**: Use the new direct API structure:
   ```python
   # Old: proxycurl.linkedin.person.get(...)
   # New: enrichlayer.person.get(...)
   ```

### Environment Variables

The compatibility layer supports both old and new environment variables:
- `PROXYCURL_API_KEY` (legacy)
- `ENRICHLAYER_API_KEY` (new)

### Benefits

- **Zero Breaking Changes**: Existing code works immediately
- **Modern Backend**: Benefits from improved EnrichLayer infrastructure  
- **Flexible Migration**: Migrate at your own pace
- **Future-Proof**: Easy path to new API structure

### Error Handling

The compatibility layer automatically maps `EnrichLayerException` to `ProxycurlException` to maintain error handling compatibility.

### Dependency Management

The compatibility module gracefully handles missing optional dependencies:
- Works with only `asyncio` installed (default)
- Automatically detects and uses `gevent` if available
- Automatically detects and uses `twisted` if available
- Provides clear error messages if `proxycurl-py` is not installed

---

For more information, visit the [Enrich Layer documentation](https://enrichlayer.com/docs) or contact our support team at support@enrichlayer.com.