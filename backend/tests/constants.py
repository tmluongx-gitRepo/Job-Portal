"""
Test constants for consistent values across test suites.

This module defines commonly used constants in tests to avoid magic values
and improve code maintainability.
"""

# HTTP Status Codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_NO_CONTENT = 204
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_CONFLICT = 409
HTTP_INTERNAL_SERVER_ERROR = 500

# Test constants
MIN_PAGE_SIZE = 2
TEST_MIN_SALARY = 100000
TEST_MIN_EXPERIENCE = 3
TEST_SKILL_COUNT = 3
TEST_EXPERIENCE_YEARS = 5

# Test Data Constants
DEFAULT_PASSWORD = "TestPass123!"
DEFAULT_ADMIN_PASSWORD = "AdminPass123!"
DEFAULT_EMPLOYER_PASSWORD = "EmpPass123!"
DEFAULT_JOB_SEEKER_PASSWORD = "JSPass123!"

# Import test users from fixtures module for backward compatibility
from tests.fixtures.test_users import TEST_USERS  # noqa: E402

__all__ = [
    "DEFAULT_ADMIN_PASSWORD",
    "DEFAULT_EMPLOYER_PASSWORD",
    "DEFAULT_JOB_SEEKER_PASSWORD",
    "DEFAULT_LIMIT",
    # Defaults
    "DEFAULT_PASSWORD",
    "DEFAULT_SKILLS",
    "DEFAULT_SKIP",
    "DEFAULT_TIMEOUT",
    "EXTENDED_SKILLS",
    "EXTENDED_SKILLS_COUNT",
    "HTTP_BAD_REQUEST",
    "HTTP_CONFLICT",
    "HTTP_CREATED",
    "HTTP_FORBIDDEN",
    "HTTP_INTERNAL_SERVER_ERROR",
    "HTTP_NOT_FOUND",
    "HTTP_NO_CONTENT",
    # HTTP Status Codes
    "HTTP_OK",
    "HTTP_UNAUTHORIZED",
    # Test constants
    "MIN_PAGE_SIZE",
    "PAGINATION_LIMIT_DEFAULT",
    "TEST_EXPERIENCE_YEARS",
    "TEST_MIN_EXPERIENCE",
    "TEST_MIN_SALARY",
    "TEST_SKILL_COUNT",
    # Test Users
    "TEST_USERS",
]

# Pagination
DEFAULT_SKIP = 0
DEFAULT_LIMIT = 100
PAGINATION_LIMIT_DEFAULT = 10

# Test Timeouts
DEFAULT_TIMEOUT = 30

# Skills
DEFAULT_SKILLS = ["Python", "FastAPI", "MongoDB"]
EXTENDED_SKILLS = ["Python", "FastAPI", "MongoDB", "React", "TypeScript"]
EXTENDED_SKILLS_COUNT = 5
