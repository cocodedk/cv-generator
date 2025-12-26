"""Tests for profile queries.

Profile query tests have been refactored into smaller, focused test files:
- test_profile_queries_save.py - Save and update tests
- test_profile_queries_get.py - Profile retrieval tests
- test_profile_queries_delete.py - Delete tests

Test helpers and mocks are located in: backend/tests/test_database/helpers/profile_queries/

Pytest will automatically discover and run all test files matching the pattern.
"""
from pytest import mark


@mark.unit
def test_profile_queries_test_suite_refactored():
    """Documentation test: Profile queries tests have been refactored into separate files."""
    # All profile query tests have been moved to focused test files:
    # - test_profile_queries_save.py
    # - test_profile_queries_get.py
    # - test_profile_queries_delete.py
    assert True
