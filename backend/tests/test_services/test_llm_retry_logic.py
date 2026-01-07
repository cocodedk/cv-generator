"""Tests for LLM retry logic."""
import httpx
from unittest.mock import Mock

from backend.services.ai.llm_client.retry_logic import (
    _should_retry_status_error,
    _should_retry_timeout,
)


class TestShouldRetryStatusError:
    """Test _should_retry_status_error function."""

    def test_retry_on_rate_limit_429(self):
        """Test that 429 (rate limit) errors should be retried."""
        response_mock = Mock()
        response_mock.status_code = 429
        error = Mock(spec=httpx.HTTPStatusError)
        error.response = response_mock

        should_retry, delay = _should_retry_status_error(error, attempt=0, max_retries=3, retry_delays=[1, 2, 4])
        assert should_retry is True
        assert delay == 1

    def test_retry_on_server_errors(self):
        """Test that 5xx server errors should be retried."""
        for status_code in [500, 502, 503]:
            response_mock = Mock()
            response_mock.status_code = status_code
            error = Mock(spec=httpx.HTTPStatusError)
            error.response = response_mock

            should_retry, delay = _should_retry_status_error(error, attempt=0, max_retries=3, retry_delays=[1, 2, 4])
            assert should_retry is True
            assert delay == 1

    def test_no_retry_on_client_errors(self):
        """Test that 4xx client errors should NOT be retried."""
        for status_code in [400, 401, 403, 404]:
            response_mock = Mock()
            response_mock.status_code = status_code
            error = Mock(spec=httpx.HTTPStatusError)
            error.response = response_mock

            should_retry, delay = _should_retry_status_error(error, attempt=0, max_retries=3, retry_delays=[1, 2, 4])
            assert should_retry is False
            assert delay == 0

    def test_no_retry_on_max_retries_exceeded(self):
        """Test that retries stop when max_retries is exceeded."""
        response_mock = Mock()
        response_mock.status_code = 429
        error = Mock(spec=httpx.HTTPStatusError)
        error.response = response_mock

        # attempt equals max_retries - 1, so should not retry
        should_retry, delay = _should_retry_status_error(error, attempt=2, max_retries=3, retry_delays=[1, 2, 4])
        assert should_retry is False
        assert delay == 0

    def test_retry_uses_correct_delay_index(self):
        """Test that retry uses the correct delay from retry_delays array."""
        response_mock = Mock()
        response_mock.status_code = 500
        error = Mock(spec=httpx.HTTPStatusError)
        error.response = response_mock

        # Test different attempt numbers
        should_retry, delay = _should_retry_status_error(error, attempt=0, max_retries=3, retry_delays=[1, 2, 4])
        assert should_retry is True
        assert delay == 1

        should_retry, delay = _should_retry_status_error(error, attempt=1, max_retries=3, retry_delays=[1, 2, 4])
        assert should_retry is True
        assert delay == 2

        should_retry, delay = _should_retry_status_error(error, attempt=2, max_retries=4, retry_delays=[1, 2, 4])
        assert should_retry is True
        assert delay == 4


class TestShouldRetryTimeout:
    """Test _should_retry_timeout function."""

    def test_retry_on_timeout_within_limit(self):
        """Test that timeouts should be retried when within limit."""
        error = Mock(spec=httpx.TimeoutException)

        should_retry, delay = _should_retry_timeout(error, attempt=0, max_retries=3, retry_delays=[1, 2, 4])
        assert should_retry is True
        assert delay == 1

        should_retry, delay = _should_retry_timeout(error, attempt=1, max_retries=3, retry_delays=[1, 2, 4])
        assert should_retry is True
        assert delay == 2

    def test_no_retry_on_timeout_max_retries_exceeded(self):
        """Test that timeouts should NOT be retried when max_retries exceeded."""
        error = Mock(spec=httpx.TimeoutException)

        should_retry, delay = _should_retry_timeout(error, attempt=2, max_retries=3, retry_delays=[1, 2, 4])
        assert should_retry is False
        assert delay == 0

    def test_retry_uses_correct_delay_index(self):
        """Test that timeout retry uses the correct delay from retry_delays array."""
        error = Mock(spec=httpx.TimeoutException)

        should_retry, delay = _should_retry_timeout(error, attempt=0, max_retries=4, retry_delays=[1, 2, 4, 8])
        assert should_retry is True
        assert delay == 1

        should_retry, delay = _should_retry_timeout(error, attempt=1, max_retries=4, retry_delays=[1, 2, 4, 8])
        assert should_retry is True
        assert delay == 2

        should_retry, delay = _should_retry_timeout(error, attempt=2, max_retries=4, retry_delays=[1, 2, 4, 8])
        assert should_retry is True
        assert delay == 4
