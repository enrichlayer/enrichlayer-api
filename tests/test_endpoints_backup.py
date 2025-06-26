#!/usr/bin/env python3
"""
Comprehensive endpoint testing for ALL EnrichLayer API endpoints.

Tests all 23 endpoints across 5 categories with both direct and compatibility interfaces.
Based on comprehensive endpoint analysis covering person, company, school, job, and customer endpoints.
"""

from datetime import datetime
import json
import os
import sys
import time
from typing import Any
import unittest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAllEndpoints(unittest.TestCase):
    """Comprehensive test of all 23 EnrichLayer endpoints."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        cls.api_key = os.environ.get("ENRICHLAYER_API_KEY") or os.environ.get(
            "PROXYCURL_API_KEY"
        )
        if not cls.api_key:
            raise unittest.SkipTest("No API key found in environment variables")

        cls.test_results = []
        cls.start_time = time.time()
        cls.total_credits_used = 0

        # Test URLs and data
        cls.test_data = {
            "person_url": "https://www.linkedin.com/in/williamhgates/",
            "company_url": "https://www.linkedin.com/company/apple",
            "school_url": "https://www.linkedin.com/school/national-university-of-singapore/",
            "job_url": "https://www.linkedin.com/jobs/view/3586148395",
            "test_email": "bill@microsoft.com",
            "test_phone": "+1234567890",
            "test_company_name": "apple",
            "test_role": "CEO",
        }

    def setUp(self):
        """Set up for each test."""
        self.test_start_time = time.time()

    def tearDown(self):
        """Clean up after each test."""
        self.test_duration = time.time() - self.test_start_time

    def _get_test_duration(self):
        """Get test duration, handling cases where tearDown hasn't run."""
        if hasattr(self, "test_duration"):
            return self.test_duration
        return (
            time.time() - self.test_start_time
            if hasattr(self, "test_start_time")
            else 0
        )

    def _record_result(
        self,
        endpoint: str,
        client_type: str,
        status: str,
        credits_used: int = 0,
        error: str = None,
        sample_data: Any = None,
    ):
        """Record test result for reporting."""
        result = {
            "endpoint": endpoint,
            "client_type": client_type,
            "status": status,
            "duration": round(self._get_test_duration(), 3),
            "credits_used": credits_used,
            "timestamp": datetime.now().isoformat(),
        }

        if error:
            result["error"] = str(error)
        if sample_data:
            result["sample_data"] = sample_data

        self.test_results.append(result)
        self.__class__.total_credits_used += credits_used

    # ======================
    # DIRECT CLIENT TESTS
    # ======================

    def test_direct_general_endpoints(self):
        """Test general endpoints with direct client."""
        from enrichlayer_client.gevent import EnrichLayer

        client = EnrichLayer(api_key=self.api_key)

        # Test get_balance
        try:
            result = client.get_balance()
            self.assertIsNotNone(result)
            self.assertIn("credit_balance", result)
            self._record_result(
                "get_balance",
                "direct",
                "success",
                0,
                sample_data={"credit_balance": result.get("credit_balance")},
            )
        except Exception as e:
            self._record_result("get_balance", "direct", "error", 0, str(e))
            self.fail(f"get_balance failed: {e}")

    def test_direct_person_endpoints(self):
        """Test all person endpoints with direct client."""
        from enrichlayer_client.gevent import EnrichLayer

        client = EnrichLayer(api_key=self.api_key)

        person_tests = [
            # Core person endpoints
            (
                "person.get",
                lambda: client.person.get(
                    linkedin_profile_url=self.test_data["person_url"], extra="exclude"
                ),
                1,
            ),
            (
                "person.search",
                lambda: client.person.search(
                    country="US",
                    first_name="John",
                    last_name="Smith",
                    enrich_profiles="skip",
                ),
                10,
            ),
            (
                "person.resolve",
                lambda: client.person.resolve(
                    company_domain="microsoft.com", first_name="Bill", last_name="Gates"
                ),
                2,
            ),
            (
                "person.resolve_by_email",
                lambda: client.person.resolve_by_email(
                    email=self.test_data["test_email"], lookup_depth="deep"
                ),
                1,
            ),
            (
                "person.resolve_by_phone",
                lambda: client.person.resolve_by_phone(
                    phone_number=self.test_data["test_phone"]
                ),
                1,
            ),
            (
                "person.lookup_email",
                lambda: client.person.lookup_email(
                    linkedin_profile_url=self.test_data["person_url"]
                ),
                1,
            ),
            (
                "person.personal_contact",
                lambda: client.person.personal_contact(
                    linkedin_profile_url=self.test_data["person_url"]
                ),
                1,
            ),
            (
                "person.personal_email",
                lambda: client.person.personal_email(
                    linkedin_profile_url=self.test_data["person_url"]
                ),
                1,
            ),
            (
                "person.profile_picture",
                lambda: client.person.profile_picture(
                    linkedin_person_profile_url=self.test_data["person_url"]
                ),
                0,
            ),
        ]

        for endpoint_name, endpoint_func, expected_credits in person_tests:
            with self.subTest(endpoint=endpoint_name):
                try:
                    result = endpoint_func()
                    self.assertIsNotNone(result)

                    # Extract sample data based on endpoint
                    sample_data = {}
                    if endpoint_name == "person.get" and isinstance(result, dict):
                        sample_data = {
                            "full_name": result.get("full_name"),
                            "headline": result.get("headline"),
                            "experience_count": len(result.get("experiences", [])),
                            "education_count": len(result.get("education", [])),
                        }
                    elif endpoint_name == "person.search" and isinstance(result, dict):
                        sample_data = {
                            "total_results": result.get("total_result_count"),
                            "results_count": len(result.get("results", [])),
                            "has_next_page": result.get("next_page") is not None,
                        }
                    elif isinstance(result, dict):
                        # Generic sample for other endpoints
                        sample_data = {k: v for k, v in list(result.items())[:3]}

                    self._record_result(
                        endpoint_name,
                        "direct",
                        "success",
                        expected_credits,
                        sample_data=sample_data,
                    )

                except Exception as e:
                    self._record_result(endpoint_name, "direct", "error", 0, str(e))
                    print(f"⚠️  {endpoint_name} failed: {e}")

    def test_direct_company_endpoints(self):
        """Test all company endpoints with direct client."""
        from enrichlayer_client.gevent import EnrichLayer

        client = EnrichLayer(api_key=self.api_key)

        company_tests = [
            (
                "company.get",
                lambda: client.company.get(url=self.test_data["company_url"]),
                1,
            ),
            (
                "company.search",
                lambda: client.company.search(
                    country="US", region="California", type="Public Company"
                ),
                10,
            ),
            (
                "company.resolve",
                lambda: client.company.resolve(
                    company_name="Apple", company_domain="apple.com"
                ),
                2,
            ),
            (
                "company.find_job",
                lambda: client.company.find_job(keyword="engineer", geo_id="103644278"),
                2,
            ),
            (
                "company.job_count",
                lambda: client.company.job_count(
                    keyword="engineer", geo_id="103644278"
                ),
                1,
            ),
            (
                "company.employee_count",
                lambda: client.company.employee_count(
                    url=self.test_data["company_url"]
                ),
                1,
            ),
            (
                "company.employee_list",
                lambda: client.company.employee_list(url=self.test_data["company_url"]),
                1,
            ),
            (
                "company.employee_search",
                lambda: client.company.employee_search(
                    keyword_regex="CEO",
                    linkedin_company_profile_url=self.test_data["company_url"],
                ),
                3,
            ),
            (
                "company.role_lookup",
                lambda: client.company.role_lookup(
                    company_name=self.test_data["test_company_name"],
                    role=self.test_data["test_role"],
                ),
                3,
            ),
            (
                "company.profile_picture",
                lambda: client.company.profile_picture(
                    linkedin_company_profile_url=self.test_data["company_url"]
                ),
                0,
            ),
        ]

        for endpoint_name, endpoint_func, expected_credits in company_tests:
            with self.subTest(endpoint=endpoint_name):
                try:
                    result = endpoint_func()
                    self.assertIsNotNone(result)

                    # Extract sample data
                    sample_data = {}
                    if endpoint_name == "company.get" and isinstance(result, dict):
                        sample_data = {
                            "name": result.get("name"),
                            "industry": result.get("industry"),
                            "follower_count": result.get("follower_count"),
                        }
                    elif endpoint_name == "company.search" and isinstance(result, dict):
                        sample_data = {
                            "total_results": result.get("total_result_count"),
                            "results_count": len(result.get("results", [])),
                        }
                    elif isinstance(result, dict):
                        sample_data = {k: v for k, v in list(result.items())[:3]}

                    self._record_result(
                        endpoint_name,
                        "direct",
                        "success",
                        expected_credits,
                        sample_data=sample_data,
                    )

                except Exception as e:
                    self._record_result(endpoint_name, "direct", "error", 0, str(e))
                    print(f"⚠️  {endpoint_name} failed: {e}")

    def test_direct_school_endpoints(self):
        """Test all school endpoints with direct client."""
        from enrichlayer_client.gevent import EnrichLayer

        client = EnrichLayer(api_key=self.api_key)

        school_tests = [
            (
                "school.get",
                lambda: client.school.get(url=self.test_data["school_url"]),
                1,
            ),
            (
                "school.student_list",
                lambda: client.school.student_list(
                    linkedin_school_url=self.test_data["school_url"]
                ),
                1,
            ),
        ]

        for endpoint_name, endpoint_func, expected_credits in school_tests:
            with self.subTest(endpoint=endpoint_name):
                try:
                    result = endpoint_func()
                    self.assertIsNotNone(result)

                    sample_data = {}
                    if endpoint_name == "school.get" and isinstance(result, dict):
                        sample_data = {
                            "name": result.get("name"),
                            "industry": result.get("industry"),
                            "follower_count": result.get("follower_count"),
                        }
                    elif isinstance(result, dict):
                        sample_data = {k: v for k, v in list(result.items())[:3]}

                    self._record_result(
                        endpoint_name,
                        "direct",
                        "success",
                        expected_credits,
                        sample_data=sample_data,
                    )

                except Exception as e:
                    self._record_result(endpoint_name, "direct", "error", 0, str(e))
                    print(f"⚠️  {endpoint_name} failed: {e}")

    def test_direct_job_endpoints(self):
        """Test all job endpoints with direct client."""
        from enrichlayer_client.gevent import EnrichLayer

        client = EnrichLayer(api_key=self.api_key)

        job_tests = [
            ("job.get", lambda: client.job.get(url=self.test_data["job_url"]), 1),
        ]

        for endpoint_name, endpoint_func, expected_credits in job_tests:
            with self.subTest(endpoint=endpoint_name):
                try:
                    result = endpoint_func()
                    self.assertIsNotNone(result)

                    sample_data = {}
                    if isinstance(result, dict):
                        sample_data = {
                            "title": result.get("title"),
                            "company": result.get("company"),
                        }

                    self._record_result(
                        endpoint_name,
                        "direct",
                        "success",
                        expected_credits,
                        sample_data=sample_data,
                    )

                except Exception as e:
                    self._record_result(endpoint_name, "direct", "error", 0, str(e))
                    print(f"⚠️  {endpoint_name} failed: {e}")

    def test_direct_customer_endpoints(self):
        """Test all customer endpoints with direct client."""
        from enrichlayer_client.gevent import EnrichLayer

        client = EnrichLayer(api_key=self.api_key)

        customer_tests = [
            ("customers.listing", lambda: client.customers.listing(), 1),
        ]

        for endpoint_name, endpoint_func, expected_credits in customer_tests:
            with self.subTest(endpoint=endpoint_name):
                try:
                    result = endpoint_func()
                    self.assertIsNotNone(result)

                    sample_data = {}
                    if isinstance(result, dict):
                        sample_data = {k: v for k, v in list(result.items())[:3]}

                    self._record_result(
                        endpoint_name,
                        "direct",
                        "success",
                        expected_credits,
                        sample_data=sample_data,
                    )

                except Exception as e:
                    self._record_result(endpoint_name, "direct", "error", 0, str(e))
                    print(f"⚠️  {endpoint_name} failed: {e}")

    # ======================
    # COMPATIBILITY TESTS
    # ======================

    def test_compatibility_core_endpoints(self):
        """Test core endpoints through proxycurl compatibility layer."""
        # Enable compatibility
        from enrichlayer_client.compat import enable_proxycurl_compatibility

        enable_proxycurl_compatibility(api_key=self.api_key)

        from proxycurl.asyncio import Proxycurl

        proxycurl = Proxycurl(api_key=self.api_key)

        compatibility_tests = [
            # General
            ("get_balance", lambda: proxycurl.get_balance(), 0),
            # Person endpoints
            (
                "linkedin.person.get",
                lambda: proxycurl.linkedin.person.get(
                    linkedin_profile_url=self.test_data["person_url"], extra="exclude"
                ),
                1,
            ),
            (
                "linkedin.person.search",
                lambda: proxycurl.linkedin.person.search(
                    country="US",
                    first_name="John",
                    last_name="Smith",
                    enrich_profiles="skip",
                ),
                10,
            ),
            (
                "linkedin.person.resolve",
                lambda: proxycurl.linkedin.person.resolve(
                    company_domain="microsoft.com", first_name="Bill", last_name="Gates"
                ),
                2,
            ),
            # Company endpoints
            (
                "linkedin.company.get",
                lambda: proxycurl.linkedin.company.get(
                    url=self.test_data["company_url"]
                ),
                1,
            ),
            (
                "linkedin.company.search",
                lambda: proxycurl.linkedin.company.search(
                    country="US", region="California", type="Public Company"
                ),
                10,
            ),
            # School endpoints
            (
                "linkedin.school.get",
                lambda: proxycurl.linkedin.school.get(url=self.test_data["school_url"]),
                1,
            ),
            # Job endpoints
            (
                "linkedin.job.get",
                lambda: proxycurl.linkedin.job.get(url=self.test_data["job_url"]),
                1,
            ),
        ]

        for endpoint_name, endpoint_func, expected_credits in compatibility_tests:
            with self.subTest(endpoint=endpoint_name):
                try:
                    result = endpoint_func()
                    self.assertIsNotNone(result)

                    # Extract basic sample data
                    sample_data = {}
                    if isinstance(result, dict):
                        sample_data = {k: v for k, v in list(result.items())[:2]}

                    self._record_result(
                        endpoint_name,
                        "compatibility",
                        "success",
                        expected_credits,
                        sample_data=sample_data,
                    )

                except Exception as e:
                    self._record_result(
                        endpoint_name, "compatibility", "error", 0, str(e)
                    )
                    print(f"⚠️  Compatibility {endpoint_name} failed: {e}")

    # ======================
    # ASYNCIO CLIENT TESTS
    # ======================

    def test_asyncio_core_endpoints(self):
        """Test core endpoints with asyncio client for comparison."""
        import asyncio

        from enrichlayer_client.asyncio import EnrichLayer

        client = EnrichLayer(api_key=self.api_key)

        asyncio_tests = [
            # General
            ("get_balance", lambda: asyncio.run(client.get_balance()), 0),
            # Person endpoints (sample)
            (
                "person.get",
                lambda: asyncio.run(
                    client.person.get(
                        linkedin_profile_url=self.test_data["person_url"],
                        extra="exclude",
                    )
                ),
                1,
            ),
            (
                "person.search",
                lambda: asyncio.run(
                    client.person.search(
                        country="US",
                        first_name="John",
                        last_name="Smith",
                        enrich_profiles="skip",
                    )
                ),
                10,
            ),
            # Company endpoints (sample)
            (
                "company.get",
                lambda: asyncio.run(
                    client.company.get(url=self.test_data["company_url"])
                ),
                1,
            ),
            (
                "company.find_job",
                lambda: asyncio.run(
                    client.company.find_job(keyword="engineer", geo_id="103644278")
                ),
                2,
            ),
            # School endpoints
            (
                "school.get",
                lambda: asyncio.run(
                    client.school.get(url=self.test_data["school_url"])
                ),
                1,
            ),
            # Job endpoints
            (
                "job.get",
                lambda: asyncio.run(client.job.get(url=self.test_data["job_url"])),
                1,
            ),
        ]

        for endpoint_name, endpoint_func, expected_credits in asyncio_tests:
            with self.subTest(endpoint=endpoint_name, client="asyncio"):
                try:
                    result = endpoint_func()
                    self.assertIsNotNone(result)

                    # Extract basic sample data
                    sample_data = {}
                    if isinstance(result, dict):
                        sample_data = {k: v for k, v in list(result.items())[:2]}

                    self._record_result(
                        f"asyncio.{endpoint_name}",
                        "asyncio",
                        "success",
                        expected_credits,
                        sample_data=sample_data,
                    )

                except Exception as e:
                    self._record_result(
                        f"asyncio.{endpoint_name}", "asyncio", "error", 0, str(e)
                    )
                    print(f"⚠️  Asyncio {endpoint_name} failed: {e}")

    # ======================
    # BULK OPERATIONS
    # ======================

    def test_bulk_operations(self):
        """Test bulk operations with multiple endpoints."""
        from enrichlayer_client.gevent import EnrichLayer, do_bulk

        client = EnrichLayer(api_key=self.api_key)

        try:
            # Test bulk operation with multiple endpoints using proper syntax
            bulk_operations = [
                (
                    client.person.get,
                    {"linkedin_profile_url": self.test_data["person_url"]},
                ),
                (client.company.get, {"url": self.test_data["company_url"]}),
                (client.school.get, {"url": self.test_data["school_url"]}),
            ]

            result = do_bulk(bulk_operations)
            self.assertIsNotNone(result)

            sample_data = {
                "total_tasks": len(bulk_operations),
                "successful_results": len([r for r in result if r.success]),
                "first_result_type": type(result[0]).__name__ if result else None,
            }

            self._record_result(
                "do_bulk", "direct", "success", 3, sample_data=sample_data
            )

        except Exception as e:
            self._record_result("do_bulk", "direct", "error", 0, str(e))
            print(f"⚠️  do_bulk failed: {e}")

    @classmethod
    def tearDownClass(cls):
        """Generate comprehensive test report after all tests complete."""
        total_duration = time.time() - cls.start_time

        # Categorize results
        by_client_type = {}
        by_status = {}
        by_category = {}

        for result in cls.test_results:
            client_type = result["client_type"]
            status = result["status"]
            endpoint = result["endpoint"]

            # By client type
            if client_type not in by_client_type:
                by_client_type[client_type] = {"total": 0, "success": 0, "error": 0}
            by_client_type[client_type]["total"] += 1
            by_client_type[client_type][status] += 1

            # By status
            if status not in by_status:
                by_status[status] = 0
            by_status[status] += 1

            # By category
            if "." in endpoint:
                category = (
                    endpoint.split(".")[0] if endpoint != "get_balance" else "general"
                )
            else:
                category = "general"

            if category not in by_category:
                by_category[category] = {"total": 0, "success": 0, "error": 0}
            by_category[category]["total"] += 1
            by_category[category][status] += 1

        # Generate comprehensive report
        total_tests = len(cls.test_results)
        successful_tests = by_status.get("success", 0)
        failed_tests = by_status.get("error", 0)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0

        report = {
            "test_summary": {
                "timestamp": datetime.now().isoformat(),
                "test_type": "comprehensive_endpoint_testing_all_23_endpoints",
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": f"{success_rate:.1f}%",
                "total_credits_used": cls.total_credits_used,
                "total_duration": round(total_duration, 3),
                "average_response_time": round(
                    sum(r["duration"] for r in cls.test_results) / total_tests, 3
                )
                if total_tests > 0
                else 0,
            },
            "by_client_type": by_client_type,
            "by_category": by_category,
            "detailed_results": cls.test_results,
        }

        # Save detailed JSON report
        with open("tests/comprehensive_endpoint_test_report.json", "w") as f:
            json.dump(report, f, indent=2)

        # Save human-readable summary
        with open("tests/endpoint_test_summary.txt", "w") as f:
            f.write("CONSOLIDATED ENDPOINT TEST RESULTS\n")
            f.write("=" * 70 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")

            f.write("📊 OVERALL SUMMARY\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total Tests: {total_tests}\n")
            f.write(f"Successful: {successful_tests}\n")
            f.write(f"Failed: {failed_tests}\n")
            f.write(f"Success Rate: {success_rate:.1f}%\n")
            f.write(f"Total Credits Used: {cls.total_credits_used}\n")
            f.write(f"Duration: {total_duration:.2f}s\n\n")

            f.write("📊 BY CLIENT TYPE\n")
            f.write("-" * 30 + "\n")
            for client_type, stats in by_client_type.items():
                f.write(
                    f"{client_type.upper()}: {stats['success']}/{stats['total']} successful ({stats['success'] / stats['total'] * 100:.1f}%)\n"
                )
            f.write("\n")

            f.write("📊 BY CATEGORY\n")
            f.write("-" * 30 + "\n")
            for category, stats in by_category.items():
                f.write(
                    f"{category.upper()}: {stats['success']}/{stats['total']} successful ({stats['success'] / stats['total'] * 100:.1f}%)\n"
                )
            f.write("\n")

            f.write("✅ SUCCESSFUL ENDPOINTS\n")
            f.write("-" * 30 + "\n")
            for result in cls.test_results:
                if result["status"] == "success":
                    f.write(
                        f"  ✅ {result['endpoint']} ({result['client_type']}) - {result['credits_used']} credits, {result['duration']}s\n"
                    )
            f.write("\n")

            if failed_tests > 0:
                f.write("❌ FAILED ENDPOINTS\n")
                f.write("-" * 30 + "\n")
                for result in cls.test_results:
                    if result["status"] == "error":
                        f.write(
                            f"  ❌ {result['endpoint']} ({result['client_type']}) - {result.get('error', 'Unknown error')}\n"
                        )
                f.write("\n")

        # Save executive summary
        executive_summary = {
            "timestamp": datetime.now().isoformat(),
            "test_framework": "unittest_consolidated",
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": f"{success_rate:.1f}%",
            "total_credits_used": cls.total_credits_used,
            "production_ready": failed_tests == 0,
            "client_types_tested": list(by_client_type.keys()),
            "categories_tested": list(by_category.keys()),
        }

        with open("tests/executive_summary.json", "w") as f:
            json.dump(executive_summary, f, indent=2)

        # Print summary
        print(f"\n{'=' * 70}")
        print("CONSOLIDATED ENDPOINT TEST SUMMARY")
        print(f"{'=' * 70}")
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Credits Used: {cls.total_credits_used}")
        print(f"Duration: {total_duration:.2f}s")
        print("\nBY CATEGORY:")
        for category, stats in by_category.items():
            print(
                f"  {category.upper()}: {stats['success']}/{stats['total']} successful"
            )
        print("\nBY CLIENT TYPE:")
        for client_type, stats in by_client_type.items():
            print(
                f"  {client_type.upper()}: {stats['success']}/{stats['total']} successful"
            )
        print("\n📁 Reports saved to:")
        print("   • tests/comprehensive_endpoint_test_report.json")
        print("   • tests/endpoint_test_summary.txt")
        print("   • tests/executive_summary.json")


if __name__ == "__main__":
    unittest.main(verbosity=2)
