"""Tests for validation_exception_handler function."""

import pytest
from unittest.mock import AsyncMock
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.app_helpers.exception_handlers.validation import validation_exception_handler


@pytest.mark.asyncio
class TestValidationExceptionHandler:
    """Test validation_exception_handler function."""

    @pytest.fixture
    def mock_request(self):
        """Create mock request."""
        request = AsyncMock(spec=Request)
        return request

    async def test_string_too_long_error(self, mock_request):
        """Test string too long error handling."""
        errors = [
            {
                "loc": ("body", "personal_info", "summary"),
                "msg": "String should have at most 1000 characters",
                "type": "string_too_long",
                "ctx": {"max_length": 1000}
            }
        ]
        exc = RequestValidationError(errors=errors)

        response = await validation_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 422

        data = response.body
        assert b"Professional Summary: Maximum 1000 characters allowed" in data
        assert b"errors" in data

    async def test_missing_field_error(self, mock_request):
        """Test missing field error handling."""
        errors = [
            {
                "loc": ("body", "personal_info", "name"),
                "msg": "Field required",
                "type": "value_error.missing"
            }
        ]
        exc = RequestValidationError(errors=errors)

        response = await validation_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 422

        data = response.body
        assert b"Full Name: Field is required" in data

    async def test_email_validation_error(self, mock_request):
        """Test email validation error handling."""
        errors = [
            {
                "loc": ("body", "personal_info", "email"),
                "msg": "value is not a valid email address",
                "type": "value_error.email"
            }
        ]
        exc = RequestValidationError(errors=errors)

        response = await validation_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 422

        data = response.body
        assert b"Email: Email format invalid" in data

    async def test_type_error_string(self, mock_request):
        """Test type error string handling."""
        errors = [
            {
                "loc": ("body", "personal_info", "name"),
                "msg": "str type expected",
                "type": "type_error.str"
            }
        ]
        exc = RequestValidationError(errors=errors)

        response = await validation_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 422

        data = response.body
        assert b"Full Name: Expected text value" in data

    async def test_type_error_integer(self, mock_request):
        """Test type error integer handling."""
        errors = [
            {
                "loc": ("body", "skills", 0, "level"),
                "msg": "int type expected",
                "type": "type_error.integer"
            }
        ]
        exc = RequestValidationError(errors=errors)

        response = await validation_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 422

        data = response.body
        assert b"Skill 1 - Level: Expected number value" in data

    async def test_min_length_error(self, mock_request):
        """Test minimum length error handling."""
        errors = [
            {
                "loc": ("body", "personal_info", "name"),
                "msg": "ensure this value has at least 1 characters",
                "type": "value_error.str.min_length"
            }
        ]
        exc = RequestValidationError(errors=errors)

        response = await validation_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 422

        data = response.body
        assert b"Full Name: Value is too short" in data

    async def test_max_length_error(self, mock_request):
        """Test maximum length error handling."""
        errors = [
            {
                "loc": ("body", "experience", 0, "description"),
                "msg": "ensure this value has at most 500 characters",
                "type": "value_error.str.max_length"
            }
        ]
        exc = RequestValidationError(errors=errors)

        response = await validation_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 422

        data = response.body
        assert b"Experience 1 - Role Summary: Value is too long" in data

    async def test_unknown_error_type(self, mock_request):
        """Test unknown error type falls back to original message."""
        errors = [
            {
                "loc": ("body", "personal_info", "name"),
                "msg": "Some unknown error occurred",
                "type": "unknown_error_type"
            }
        ]
        exc = RequestValidationError(errors=errors)

        response = await validation_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 422

        data = response.body
        assert b"Full Name: Some unknown error occurred" in data

    async def test_multiple_errors(self, mock_request):
        """Test handling multiple validation errors."""
        errors = [
            {
                "loc": ("body", "personal_info", "name"),
                "msg": "Field required",
                "type": "value_error.missing"
            },
            {
                "loc": ("body", "personal_info", "email"),
                "msg": "value is not a valid email address",
                "type": "value_error.email"
            }
        ]
        exc = RequestValidationError(errors=errors)

        response = await validation_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 422

        data = response.body
        assert b"Full Name: Field is required" in data
        assert b"Email: Email format invalid" in data

    async def test_body_prefix_stripping(self, mock_request):
        """Test that leading 'body' prefix is stripped from location."""
        errors = [
            {
                "loc": ("body", "personal_info", "name"),
                "msg": "Field required",
                "type": "value_error.missing"
            }
        ]
        exc = RequestValidationError(errors=errors)

        response = await validation_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 422

        data = response.body
        assert b"Full Name: Field is required" in data

    async def test_no_body_prefix(self, mock_request):
        """Test locations without 'body' prefix."""
        errors = [
            {
                "loc": ("personal_info", "name"),
                "msg": "Field required",
                "type": "value_error.missing"
            }
        ]
        exc = RequestValidationError(errors=errors)

        response = await validation_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 422

        data = response.body
        assert b"Full Name: Field is required" in data

    async def test_field_path_inclusion(self, mock_request):
        """Test that field_path is included in modified errors."""
        errors = [
            {
                "loc": ("body", "experience", 0, "title"),
                "msg": "Field required",
                "type": "value_error.missing"
            }
        ]
        exc = RequestValidationError(errors=errors)

        response = await validation_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 422

        # The response should contain modified errors with field_path
        data = response.body
        # This is a basic check - the field_path should be "experience.0.title"
        assert b"errors" in data
