"""Cover letter prompt building utilities."""


def _build_cover_letter_prompt(
    profile_summary: str,
    job_description: str,
    company_name: str,
    hiring_manager_name: str | None,
    tone: str,
    relevance_reasoning: str | None = None,
    llm_instructions: str | None = None,
) -> str:
    """Build the LLM prompt for cover letter generation."""
    salutation = (
        f"Dear {hiring_manager_name},"
        if hiring_manager_name
        else "Dear Hiring Manager,"
    )

    tone_instructions = {
        "professional": "Use a formal, professional tone. Focus on achievements and qualifications.",
        "enthusiastic": "Use an energetic, positive tone while remaining professional. Show genuine excitement about the role.",
        "conversational": "Use a friendly, approachable tone. Be personable while maintaining professionalism.",
    }

    tone_guide = tone_instructions.get(tone, tone_instructions["professional"])

    reasoning_section = ""
    if relevance_reasoning:
        reasoning_section = f"\n\nRELEVANCE CONTEXT:\n{relevance_reasoning}\n\nThis explains why these specific experiences and skills were selected as most relevant to this role."

    custom_instructions_section = ""
    if llm_instructions:
        custom_instructions_section = f"\n\nADDITIONAL INSTRUCTIONS:\n{llm_instructions}\n\nPlease follow these additional instructions when writing the cover letter."

    prompt = f"""You are a professional cover letter writer. Generate a compelling cover letter based on the following information.

PROFILE INFORMATION:
{profile_summary}

JOB DESCRIPTION:
{job_description}

COMPANY: {company_name}

SALUTATION: {salutation}

TONE: {tone_guide}{reasoning_section}{custom_instructions_section}

REQUIREMENTS:
1. Write a professional cover letter (3-4 paragraphs, approximately 300-400 words)
2. Opening paragraph: Hook that references the specific role and company
3. Body paragraphs (2-3): Match key achievements and skills from the profile to job requirements
4. Closing paragraph: Express enthusiasm and call to action
5. Use ONLY facts, achievements, and skills from the profile information above
6. DO NOT fabricate metrics, dates, or achievements not present in the profile
7. If specific information is missing, use general statements without making up details
8. Format the letter professionally with proper spacing

Return ONLY the cover letter body text (no header, date, or signature - those will be added separately). Start directly with the salutation and end with a professional closing like "Sincerely" or "Best regards"."""

    return prompt
