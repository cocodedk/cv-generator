"""Tests for LLM client."""
import pytest
from unittest.mock import patch, AsyncMock
import httpx
from backend.services.ai.llm_client import LLMClient, get_llm_client


@pytest.fixture
def llm_client():
    """Create LLM client instance for testing."""
    with patch.dict(
        "os.environ",
        {
            "AI_ENABLED": "true",
            "AI_BASE_URL": "https://api.openai.com/v1",
            "AI_API_KEY": "test-key",
            "AI_MODEL": "gpt-3.5-turbo",
            "AI_TEMPERATURE": "0.7",
            "AI_REQUEST_TIMEOUT_S": "30",
        },
    ):
        # Reset singleton
        import backend.services.ai.llm_client as llm_module

        llm_module._llm_client = None
        yield LLMClient()


class TestLLMClient:
    """Test LLM client functionality."""

    def test_is_configured_true(self, llm_client):
        """Test is_configured returns True when properly configured."""
        assert llm_client.is_configured() is True

    def test_is_configured_false_when_disabled(self):
        """Test is_configured returns False when AI_ENABLED is false."""
        with patch.dict("os.environ", {"AI_ENABLED": "false"}):
            import backend.services.ai.llm_client as llm_module

            llm_module._llm_client = None
            client = LLMClient()
            assert client.is_configured() is False

    def test_is_configured_false_when_missing_url(self):
        """Test is_configured returns False when base URL is missing."""
        with patch.dict("os.environ", {"AI_BASE_URL": "", "AI_ENABLED": "true"}):
            import backend.services.ai.llm_client as llm_module

            llm_module._llm_client = None
            client = LLMClient()
            assert client.is_configured() is False

    def test_is_configured_false_when_missing_key(self):
        """Test is_configured returns False when API key is missing."""
        with patch.dict("os.environ", {"AI_API_KEY": "", "AI_ENABLED": "true"}):
            import backend.services.ai.llm_client as llm_module

            llm_module._llm_client = None
            client = LLMClient()
            assert client.is_configured() is False

    @pytest.mark.asyncio
    async def test_rewrite_text_success(self, llm_client):
        """Test successful text rewrite."""
        mock_response = {
            "choices": [{"message": {"content": "Rewritten text from LLM"}}]
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response_obj = AsyncMock()
            # json() should return the value directly, not a coroutine
            mock_response_obj.json = lambda: mock_response
            mock_response_obj.raise_for_status = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response_obj)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            result = await llm_client.rewrite_text("Original text", "Make it better")

            assert result == "Rewritten text from LLM"
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == "https://api.openai.com/v1/chat/completions"
            assert call_args[1]["headers"]["Authorization"] == "Bearer test-key"
            assert call_args[1]["json"]["model"] == "gpt-3.5-turbo"
            assert call_args[1]["json"]["messages"][0]["role"] == "system"
            assert call_args[1]["json"]["messages"][1]["role"] == "user"
            assert "Make it better" in call_args[1]["json"]["messages"][1]["content"]
            assert "Original text" in call_args[1]["json"]["messages"][1]["content"]

    @pytest.mark.asyncio
    async def test_rewrite_text_not_configured(self):
        """Test rewrite_text raises ValueError when not configured."""
        with patch.dict("os.environ", {"AI_ENABLED": "false"}):
            import backend.services.ai.llm_client as llm_module

            llm_module._llm_client = None
            client = LLMClient()

            with pytest.raises(ValueError, match="LLM is not configured"):
                await client.rewrite_text("text", "prompt")

    @pytest.mark.asyncio
    async def test_rewrite_text_http_error(self, llm_client):
        """Test rewrite_text handles HTTP errors."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response_obj = AsyncMock()
            # raise_for_status is synchronous, not async
            error = httpx.HTTPError("API Error")

            def raise_error():
                raise error

            mock_response_obj.raise_for_status = raise_error
            mock_client.post = AsyncMock(return_value=mock_response_obj)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            with pytest.raises(httpx.HTTPError) as exc_info:
                await llm_client.rewrite_text("text", "prompt")
            assert str(exc_info.value) == "API Error"

    @pytest.mark.asyncio
    async def test_rewrite_text_invalid_response(self, llm_client):
        """Test rewrite_text handles invalid API response."""
        mock_response = {"choices": []}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response_obj = AsyncMock()
            mock_response_obj.json = lambda: mock_response
            mock_response_obj.raise_for_status = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response_obj)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            with pytest.raises(ValueError, match="Invalid response from LLM API"):
                await llm_client.rewrite_text("text", "prompt")

    @pytest.mark.asyncio
    async def test_rewrite_text_strips_whitespace(self, llm_client):
        """Test rewrite_text strips whitespace from response."""
        mock_response = {
            "choices": [{"message": {"content": "  Rewritten text  \n\n"}}]
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response_obj = AsyncMock()
            mock_response_obj.json = lambda: mock_response
            mock_response_obj.raise_for_status = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response_obj)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            result = await llm_client.rewrite_text("text", "prompt")
            assert result == "Rewritten text"

    @pytest.mark.asyncio
    async def test_generate_text_success_with_custom_system_prompt(self, llm_client):
        """Test successful text generation with custom system prompt."""
        mock_response = {
            "choices": [{"message": {"content": "Generated text from LLM"}}]
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response_obj = AsyncMock()
            # json() should return the value directly, not a coroutine
            mock_response_obj.json = lambda: mock_response
            mock_response_obj.raise_for_status = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response_obj)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            result = await llm_client.generate_text("Generate a story", "You are a creative writer.")

            assert result == "Generated text from LLM"
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == "https://api.openai.com/v1/chat/completions"
            assert call_args[1]["headers"]["Authorization"] == "Bearer test-key"
            assert call_args[1]["json"]["model"] == "gpt-3.5-turbo"
            assert call_args[1]["json"]["messages"][0]["role"] == "system"
            assert call_args[1]["json"]["messages"][0]["content"] == "You are a creative writer."
            assert call_args[1]["json"]["messages"][1]["role"] == "user"
            assert call_args[1]["json"]["messages"][1]["content"] == "Generate a story"

    @pytest.mark.asyncio
    async def test_generate_text_success_with_default_system_prompt(self, llm_client):
        """Test successful text generation with default system prompt."""
        mock_response = {
            "choices": [{"message": {"content": "Generated text from LLM"}}]
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response_obj = AsyncMock()
            mock_response_obj.json = lambda: mock_response
            mock_response_obj.raise_for_status = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response_obj)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            result = await llm_client.generate_text("Generate a story")

            assert result == "Generated text from LLM"
            call_args = mock_client.post.call_args
            assert call_args[1]["json"]["messages"][0]["content"] == "You are a helpful assistant. Follow the user's instructions carefully."

    @pytest.mark.asyncio
    async def test_generate_text_not_configured(self):
        """Test generate_text raises ValueError when not configured."""
        with patch.dict("os.environ", {"AI_ENABLED": "false"}):
            import backend.services.ai.llm_client as llm_module

            llm_module._llm_client = None
            client = LLMClient()

            with pytest.raises(ValueError, match="LLM is not configured"):
                await client.generate_text("prompt")

    @pytest.mark.asyncio
    async def test_generate_text_http_error(self, llm_client):
        """Test generate_text handles HTTP errors."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response_obj = AsyncMock()
            error = httpx.HTTPError("API Error")

            def raise_error():
                raise error

            mock_response_obj.raise_for_status = raise_error
            mock_client.post = AsyncMock(return_value=mock_response_obj)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            with pytest.raises(httpx.HTTPError) as exc_info:
                await llm_client.generate_text("prompt")
            assert str(exc_info.value) == "API Error"

    @pytest.mark.asyncio
    async def test_generate_text_invalid_response(self, llm_client):
        """Test generate_text handles invalid API response."""
        mock_response = {"choices": []}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response_obj = AsyncMock()
            mock_response_obj.json = lambda: mock_response
            mock_response_obj.raise_for_status = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response_obj)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            with pytest.raises(ValueError, match="Invalid response from LLM API"):
                await llm_client.generate_text("prompt")


class TestGetLLMClient:
    """Test get_llm_client singleton."""

    def test_get_llm_client_returns_singleton(self):
        """Test get_llm_client returns the same instance."""
        import backend.services.ai.llm_client as llm_module

        llm_module._llm_client = None

        client1 = get_llm_client()
        client2 = get_llm_client()

        assert client1 is client2
