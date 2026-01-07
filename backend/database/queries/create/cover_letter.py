"""Cover letter node creation."""


def create_cover_letter_node(
    tx,
    cover_letter_id: str,
    created_at: str,
    job_description: str,
    company_name: str,
    hiring_manager_name: str | None,
    company_address: str | None,
    tone: str,
    cover_letter_html: str,
    cover_letter_text: str,
    highlights_used: list[str],
    selected_experiences: list[str],
    selected_skills: list[str],
):
    """Create cover letter node."""
    query = """
    CREATE (cl:CoverLetter {
        id: $cover_letter_id,
        created_at: $created_at,
        updated_at: $created_at,
        job_description: $job_description,
        company_name: $company_name,
        hiring_manager_name: $hiring_manager_name,
        company_address: $company_address,
        tone: $tone,
        cover_letter_html: $cover_letter_html,
        cover_letter_text: $cover_letter_text,
        highlights_used: $highlights_used,
        selected_experiences: $selected_experiences,
        selected_skills: $selected_skills
    })
    RETURN cl
    """
    result = tx.run(
        query,
        cover_letter_id=cover_letter_id,
        created_at=created_at,
        job_description=job_description,
        company_name=company_name,
        hiring_manager_name=hiring_manager_name,
        company_address=company_address,
        tone=tone,
        cover_letter_html=cover_letter_html,
        cover_letter_text=cover_letter_text,
        highlights_used=highlights_used,
        selected_experiences=selected_experiences,
        selected_skills=selected_skills,
    )
    result.consume()
    return cover_letter_id
