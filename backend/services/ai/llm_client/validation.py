"""Configuration validation utilities."""


def _validate_configuration(self) -> None:
    """Validate LLM configuration and raise error if missing."""
    if not self.is_configured():
        missing = []
        if not self.enabled:
            missing.append("AI_ENABLED=true")
        if not self.base_url:
            missing.append("AI_BASE_URL")
        if not self.api_key:
            missing.append("AI_API_KEY")
        raise ValueError(
            f"LLM is not configured. Missing: {', '.join(missing)}. "
            f"Set these in .env file and ensure docker-compose.yml passes them to the container."
        )
