"""
Test fixtures package for organizing test resources.

This package contains:
- test_users.py: Permanent test user credentials
- user_fixtures.py: User-related pytest fixtures
"""

from tests.fixtures.test_users import TEST_USERS

__all__ = ["TEST_USERS"]
