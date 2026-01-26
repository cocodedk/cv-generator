"""Response validation helpers for API testing."""
import json
from typing import Any, Dict


def assert_validation_error_response(response, expected_status: int = 422) -> Dict[str, Any]:
    """Assert that a response is a valid validation error response and return parsed data.

    Args:
        response: The HTTP response object
        expected_status: Expected HTTP status code (default 422)

    Returns:
        Parsed JSON response data

    Raises:
        AssertionError: If response is not valid or doesn't meet expectations
    """
    assert response.status_code == expected_status, f"Expected status {expected_status}, got {response.status_code}"

    # Ensure response is valid JSON (this would catch serialization errors)
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        raise AssertionError(f"Response is not valid JSON: {e}")

    # Validate standard error response structure
    assert "detail" in data, "Error response missing 'detail' field"
    assert "errors" in data, "Error response missing 'errors' field"

    # Ensure detail is a list with content
    assert isinstance(data["detail"], list), "'detail' field should be a list"
    assert len(data["detail"]) > 0, "'detail' field should not be empty"

    # Ensure errors is a list
    assert isinstance(data["errors"], list), "'errors' field should be a list"
    assert len(data["errors"]) > 0, "'errors' field should not be empty"

    return data


def assert_success_response(response, expected_status: int = 200) -> Dict[str, Any]:
    """Assert that a response is a valid success response and return parsed data.

    Args:
        response: The HTTP response object
        expected_status: Expected HTTP status code (default 200)

    Returns:
        Parsed JSON response data

    Raises:
        AssertionError: If response is not valid or doesn't meet expectations
    """
    assert response.status_code == expected_status, f"Expected status {expected_status}, got {response.status_code}"

    # Ensure response is valid JSON
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        raise AssertionError(f"Response is not valid JSON: {e}")

    # Validate standard success response structure
    assert "status" in data, "Success response missing 'status' field"
    assert data["status"] == "success", f"Expected status 'success', got '{data['status']}'"

    return data


def assert_error_response(response, expected_status: int, expected_message: str = None) -> Dict[str, Any]:
    """Assert that a response is a valid error response and return parsed data.

    Args:
        response: The HTTP response object
        expected_status: Expected HTTP status code
        expected_message: Optional expected error message

    Returns:
        Parsed JSON response data

    Raises:
        AssertionError: If response is not valid or doesn't meet expectations
    """
    assert response.status_code == expected_status, f"Expected status {expected_status}, got {response.status_code}"

    # Ensure response is valid JSON
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        raise AssertionError(f"Response is not valid JSON: {e}")

    # Validate error response structure
    assert "detail" in data, "Error response missing 'detail' field"

    if expected_message:
        assert data["detail"] == expected_message, f"Expected message '{expected_message}', got '{data['detail']}'"

    return data
