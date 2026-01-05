"""LLM-based selection of relevant profile content for cover letters."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import List
import httpx

from backend.models import ProfileData
from backend.services.ai.llm_client import LLMClient

logger = logging.getLogger(__name__)


@dataclass
class SelectedContent:
    """Selected relevant content from profile for cover letter."""

    experience_indices: List[int]  # Which experiences are most relevant
    skill_names: List[str]  # Which skills to highlight
    key_highlights: List[str]  # Specific achievements to mention
    relevance_reasoning: str  # Why these were selected


def _format_profile_for_selection(profile: ProfileData) -> str:
    """Format profile data for LLM selection analysis."""
    lines = []

    # Index experiences for reference
    lines.append("EXPERIENCES:")
    for idx, exp in enumerate(profile.experience):
        exp_lines = [f"[{idx}] {exp.title} at {exp.company}"]
        if exp.description:
            exp_lines.append(f"    Description: {exp.description}")
        if exp.start_date:
            exp_lines.append(
                f"    Dates: {exp.start_date} - {exp.end_date or 'Present'}"
            )
        for project in exp.projects:
            if project.name:
                exp_lines.append(f"    Project: {project.name}")
            if project.technologies:
                exp_lines.append(
                    f"      Technologies: {', '.join(project.technologies)}"
                )
            if project.highlights:
                for highlight in project.highlights:
                    exp_lines.append(f"      • {highlight}")
        lines.extend(exp_lines)
        lines.append("")

    # List all skills
    if profile.skills:
        skill_names = [s.name for s in profile.skills]
        lines.append(f"SKILLS: {', '.join(skill_names)}")

    return "\n".join(lines)


def _build_selection_prompt(profile_text: str, job_description: str) -> str:
    """Build prompt for LLM to select relevant content."""
    prompt = f"""You are analyzing a job application. Your task is to identify which parts of the candidate's profile are MOST relevant to this specific job.

JOB DESCRIPTION:
{job_description[:4000]}

CANDIDATE PROFILE:
{profile_text}

Analyze the job requirements and the candidate's profile. Identify:
1. Which experiences (by index) are most relevant to this job
2. Which skills match the job requirements best
3. Which specific achievements/highlights demonstrate fit

Return your analysis as a JSON object with this exact structure:
{{
  "experience_indices": [0, 2, 3],
  "skill_names": ["Django", "Node.js", "Python", "REST APIs"],
  "key_highlights": [
    "Built scalable Django REST API serving 1M+ requests",
    "Led migration from LAMP to Node.js microservices"
  ],
  "relevance_reasoning": "Brief explanation of why these items were selected"
}}

IMPORTANT:
- Only include experiences that are genuinely relevant to THIS job
- Prioritize skills that match job requirements (e.g., Django/Node.js over LAMP if job mentions Python/JavaScript)
- Select highlights that demonstrate fit for the role
- Be selective - quality over quantity
- Return ONLY valid JSON, no markdown or extra text"""

    return prompt


async def select_relevant_content(  # noqa: C901
    profile: ProfileData,
    job_description: str,
    llm_client: LLMClient,
) -> SelectedContent:
    """
    Use LLM to identify most relevant profile content for the job.

    Args:
        profile: Full profile data
        job_description: Job description text
        llm_client: Configured LLM client

    Returns:
        SelectedContent with indices and names of relevant items

    Raises:
        ValueError: If LLM call fails or returns invalid JSON
    """
    # Format profile for analysis
    profile_text = _format_profile_for_selection(profile)

    # Build selection prompt
    prompt = _build_selection_prompt(profile_text, job_description)

    # Call LLM for structured selection
    try:
        system_prompt = (
            "You are a career advisor analyzing job applications. "
            "Return ONLY valid JSON, no explanations or markdown."
        )

        user_message = prompt

        payload = {
            "model": llm_client.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "max_completion_tokens": 1000,
        }

        # Only include temperature for models that support it
        if not llm_client._is_reasoning_model():
            payload["temperature"] = 0.3  # Lower temperature for consistent selection

        headers = {
            "Authorization": f"Bearer {llm_client.api_key}",
            "Content-Type": "application/json",
        }

        url = f"{llm_client.base_url}/chat/completions"

        async with httpx.AsyncClient(timeout=llm_client.timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()

            if "choices" not in result or not result["choices"]:
                raise ValueError("Invalid response from LLM API")

            content = result["choices"][0]["message"]["content"].strip()

            # Parse JSON response
            # Remove markdown code blocks if present
            if content.startswith("```"):
                # Extract JSON from code block
                lines = content.split("\n")
                json_start = None
                json_end = None
                for i, line in enumerate(lines):
                    if line.strip().startswith("```"):
                        if json_start is None:
                            json_start = i + 1
                        else:
                            json_end = i
                            break
                if json_start is not None and json_end is not None:
                    content = "\n".join(lines[json_start:json_end])
                elif json_start is not None:
                    content = "\n".join(lines[json_start:])

            # Parse JSON
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM JSON response: {content[:200]}")
                raise ValueError(f"LLM returned invalid JSON: {str(e)}") from e

            # Validate and extract data
            experience_indices = data.get("experience_indices", [])
            skill_names = data.get("skill_names", [])
            key_highlights = data.get("key_highlights", [])
            relevance_reasoning = data.get(
                "relevance_reasoning", "Selected based on job requirements"
            )

            # Validate indices are within bounds
            max_idx = len(profile.experience) - 1
            experience_indices = [
                idx
                for idx in experience_indices
                if isinstance(idx, int) and 0 <= idx <= max_idx
            ]

            # Validate skills exist in profile
            profile_skill_names = {s.name.lower() for s in profile.skills}
            skill_names = [
                skill
                for skill in skill_names
                if isinstance(skill, str) and skill.lower() in profile_skill_names
            ]

            return SelectedContent(
                experience_indices=experience_indices,
                skill_names=skill_names,
                key_highlights=key_highlights
                if isinstance(key_highlights, list)
                else [],
                relevance_reasoning=relevance_reasoning
                if isinstance(relevance_reasoning, str)
                else "",
            )

    except httpx.HTTPError as e:
        logger.error(f"LLM API request failed during selection: {e}", exc_info=True)
        raise ValueError(f"Failed to select relevant content: {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected error during content selection: {e}", exc_info=True)
        raise ValueError(f"Failed to select relevant content: {str(e)}") from e
