"""Request building utilities."""


def _build_payload(self, text: str, prompt: str) -> dict:
    """Build API request payload."""
    system_prompt = (
        "You are a helpful writing assistant. Rewrite the provided text according to the user's instructions. "
        "Return only the rewritten text, without any explanations or markdown formatting."
    )

    user_message = f"{prompt}\n\nText to rewrite:\n{text}"

    payload = {
        "model": self.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "max_completion_tokens": 2000,
    }

    # Only include temperature for models that support it
    # Reasoning models (o1, o3, gpt-5.x) don't support temperature
    if not _is_reasoning_model(self):
        payload["temperature"] = self.temperature

    return payload


def _is_reasoning_model(self) -> bool:
    """Check if the model is a reasoning model that doesn't support temperature."""
    model_lower = self.model.lower()
    # Reasoning models: o1, o3, gpt-5.x series don't support temperature
    reasoning_patterns = ("o1", "o3", "gpt-5")
    return any(pattern in model_lower for pattern in reasoning_patterns)
