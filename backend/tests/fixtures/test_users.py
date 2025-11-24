"""
Permanent Test User Credentials.

These users are created once in Supabase and reused across all test runs.
They are automatically enabled at the start of each test session and disabled
at the end for security.

SECURITY NOTE:
- All test accounts are banned (disabled) outside of test sessions
- This prevents unauthorized use even if credentials are exposed
- Accounts are auto-enabled when tests start via conftest.py

Setup:
    To create these users in Supabase, run:
    ```bash
    cd backend
    python -m tests.setup_test_users
    ```

See: tests/SETUP_NEW_TEST_USERS.md for more details.
"""

# Permanent Test Users (created once in Supabase, reused across all tests)
TEST_USERS = {
    "job_seeker": {
        "email": "test.jobseeker@yourapp.com",
        "password": "TestJobSeeker123!",
        "account_type": "job_seeker",
        "purpose": "Primary job seeker for single-user tests",
    },
    "job_seeker_2": {
        "email": "test.jobseeker2@yourapp.com",
        "password": "TestJobSeeker2123!",
        "account_type": "job_seeker",
        "purpose": "Secondary job seeker for cross-user authorization tests",
    },
    "employer": {
        "email": "test.employer@yourapp.com",
        "password": "TestEmployer123!",
        "account_type": "employer",
        "purpose": "Primary employer for single-user tests",
    },
    "employer_2": {
        "email": "test.employer2@yourapp.com",
        "password": "TestEmployer2123!",
        "account_type": "employer",
        "purpose": "Secondary employer for cross-user authorization tests",
    },
    "admin": {
        "email": "test.admin@yourapp.com",
        "password": "TestAdmin123!",
        "account_type": "admin",
        "purpose": "Admin user for testing admin-level permissions",
    },
}
