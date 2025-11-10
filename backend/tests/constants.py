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

# Test Data Constants
DEFAULT_PASSWORD = "TestPass123!"
DEFAULT_ADMIN_PASSWORD = "AdminPass123!"
DEFAULT_EMPLOYER_PASSWORD = "EmpPass123!"
DEFAULT_JOB_SEEKER_PASSWORD = "JSPass123!"

# Permanent Test Users (created once in Supabase, reused across all tests)
TEST_USERS = {
    "job_seeker": {
        "email": "test.jobseeker@yourapp.com",
        "password": "TestJobSeeker123!",
        "account_type": "job_seeker",
    },
    "employer": {
        "email": "test.employer@yourapp.com",
        "password": "TestEmployer123!",
        "account_type": "employer",
    },
    "admin": {
        "email": "test.admin@yourapp.com",
        "password": "TestAdmin123!",
        "account_type": "admin",
    },
}

# Pagination
DEFAULT_SKIP = 0
DEFAULT_LIMIT = 100

# Test Timeouts
DEFAULT_TIMEOUT = 30

# Skills
DEFAULT_SKILLS = ["Python", "FastAPI", "MongoDB"]
EXTENDED_SKILLS = ["Python", "FastAPI", "MongoDB", "React", "TypeScript"]
EXTENDED_SKILLS_COUNT = 5
