"""Text tailoring and validation utilities."""

import re

# Character limits for different CV fields (plain text, not HTML)
MAX_DESCRIPTION_CHARS = 350  # Leave buffer for the 300 char model limit
MAX_HIGHLIGHT_CHARS = 250


def _strip_html(text: str) -> str:
    """Strip HTML tags and decode entities to get plain text length."""
    plain = re.sub(r"<[^>]+>", "", text)
    plain = plain.replace("&nbsp;", " ")
    plain = plain.replace("&amp;", "&")
    plain = plain.replace("&lt;", "<")
    plain = plain.replace("&gt;", ">")
    plain = plain.replace("&quot;", '"')
    plain = plain.replace("&#39;", "'")
    plain = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), plain)
    return plain


def _get_max_chars(context: str) -> int | None:
    """Get max character limit based on context type."""
    if "description" in context:
        return MAX_DESCRIPTION_CHARS
    elif "bullet" in context or "highlight" in context:
        return MAX_HIGHLIGHT_CHARS
    return None


async def _tailor_text(
    llm_client,
    original_text: str,
    job_description: str,
    context: str,
    additional_context: str | None = None,
) -> str:
    """
    Tailor a single piece of text using LLM.

    Args:
        llm_client: Configured LLM client
        original_text: Text to tailor
        job_description: Job description context
        context: Description of what this text is (for error handling)
        additional_context: Optional additional achievements or context to incorporate

    Returns:
        Tailored text, or original if tailoring fails
    """
    if not original_text or not original_text.strip():
        return original_text

    max_chars = _get_max_chars(context)
    length_instruction = ""
    if max_chars:
        length_instruction = f"\n- Keep the rewritten text under {max_chars} characters (CRITICAL - do not exceed this limit)"

    additional_context_section = ""
    if additional_context and additional_context.strip():
        additional_context_section = f"""

Additional achievements/context to incorporate:
{additional_context}
"""

    user_prompt = f"""Job Description:
{job_description}{additional_context_section}

Original {context}:
{original_text}

CRITICAL: Reword the {context} above to better match the job description.

RULES:
- Use ONLY facts, metrics, technologies, and achievements that appear in the original text above
- You may rephrase and reorder emphasis, but DO NOT add anything new
- If the original says "improved performance", do NOT say "improved performance by 30%"
- If you cannot tailor without adding new claims, return the original text unchanged{length_instruction}

Return ONLY the reworded text, no explanations."""

    tailored = await llm_client.rewrite_text(original_text, user_prompt)

    # Validate that we got something back
    if not tailored or not tailored.strip():
        raise ValueError(f"LLM returned empty result for {context}")

    tailored = tailored.strip()

    # Validate length constraint
    if max_chars:
        plain_length = len(_strip_html(tailored))
        if plain_length > max_chars + 20:  # Small buffer for minor overruns
            raise ValueError(
                f"LLM result for {context} exceeds limit ({plain_length} > {max_chars})"
            )

    return tailored
