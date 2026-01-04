# Cover Letter Mentioning Irrelevant Technologies

## Issue Description

The cover letter generator is mentioning technologies (e.g., LAMP) that are not very relevant to the job description, when more suitable experience exists (e.g., Django, Node.js).

## Root Cause Analysis

### Problem: No Intelligent Selection Logic

The cover letter generator (`backend/services/ai/cover_letter.py`) does **NOT** use intelligent selection/scoring logic to filter profile data before sending it to the LLM. Instead, it uses simple chronological slicing:

```20:61:backend/services/ai/cover_letter.py
def _format_profile_summary(profile: ProfileData) -> str:  # noqa: C901
    """Format profile data into a summary for LLM context."""
    lines = []

    # Personal info
    if profile.personal_info.name:
        lines.append(f"Name: {profile.personal_info.name}")
    if profile.personal_info.title:
        lines.append(f"Title: {profile.personal_info.title}")

    # Experience highlights
    if profile.experience:
        lines.append("\nExperience:")
        for exp in profile.experience[:5]:  # Limit to top 5
            exp_lines = [f"  - {exp.title} at {exp.company}"]
            if exp.description:
                exp_lines.append(f"    Description: {exp.description}")
            for project in exp.projects[:2]:  # Top 2 projects per experience
                if project.name:
                    exp_lines.append(f"    Project: {project.name}")
                if project.highlights:
                    for highlight in project.highlights[:3]:  # Top 3 highlights
                        exp_lines.append(f"      • {highlight}")
            lines.extend(exp_lines)

    # Education
    if profile.education:
        lines.append("\nEducation:")
        for edu in profile.education[:2]:  # Top 2
            edu_line = f"  - {edu.degree}"
            if edu.institution:
                edu_line += f" from {edu.institution}"
            if edu.year:
                edu_line += f" ({edu.year})"
            lines.append(edu_line)

    # Skills
    if profile.skills:
        skill_names = [s.name for s in profile.skills[:15]]  # Top 15 skills
        lines.append(f"\nSkills: {', '.join(skill_names)}")

    return "\n".join(lines)
```

**Key Issues:**
1. `profile.experience[:5]` - Takes first 5 experiences chronologically, not by relevance
2. `exp.projects[:2]` - Takes first 2 projects per experience, not scored
3. `project.highlights[:3]` - Takes first 3 highlights, not scored
4. `profile.skills[:15]` - Takes first 15 skills, not scored

### Comparison: CV Draft Generator Uses Intelligent Selection

The CV draft generator (`backend/services/ai/draft.py`) **DOES** use intelligent selection:

```18:24:backend/services/ai/draft.py
async def generate_cv_draft(profile: ProfileData, request: AIGenerateCVRequest) -> AIGenerateCVResponse:
    spec = build_target_spec(request.job_description)

    max_experiences = request.max_experiences or 4
    selected_experiences, warnings = select_experiences(profile.experience, spec, max_experiences)
    selected_education = select_education(profile.education, spec, max_education=2)
    selected_skills = select_skills(profile.skills, spec, selected_experiences)
```

The `select_experiences()` function:
- Scores each experience based on keyword matches with job description
- Considers technologies used in projects
- Weights by recency, seniority signals, and responsibility matches
- Returns only the **most relevant** experiences

```12:36:backend/services/ai/selection.py
def select_experiences(
    experiences: List[Experience],
    spec,
    max_experiences: int,
) -> Tuple[List[Experience], List[str]]:
    if not experiences:
        return [], ["Profile has no experiences; draft will be sparse."]

    scored: List[Tuple[float, Experience]] = []
    for experience in experiences:
        exp_score = score_item(
            text_parts=[experience.title, experience.company, experience.description or ""],
            technologies=[tech for project in experience.projects for tech in project.technologies],
            start_date=experience.start_date,
            spec=spec,
        ).value
        scored.append((exp_score, experience))

    top_experiences = [experience for _, experience in top_n_scored(scored, max_experiences)]
    trimmed: List[Experience] = []
    for experience in top_experiences:
        projects = _select_projects(experience, spec, max_projects=2)
        trimmed.append(Experience(**experience.model_dump(exclude={"projects"}), projects=projects))

    return trimmed, []
```

### Why This Causes the Problem

When the cover letter generator sends **all** profile data (including old LAMP experience) to the LLM:

1. **Information Overload**: The LLM receives too much irrelevant data mixed with relevant data
2. **No Prioritization**: The LLM doesn't know which experiences are more relevant to the job
3. **Chronological Bias**: Older experiences (like LAMP) may appear first in the profile and get mentioned
4. **Technology Confusion**: The LLM sees both LAMP and Django/Node.js and may mention both, or prioritize incorrectly

The LLM prompt does instruct it to match skills, but without pre-filtering, it's working with a noisy dataset:

```100:110:backend/services/ai/cover_letter.py
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
```

## Solution

### Recommended Fix

Modify `generate_cover_letter()` to use the same intelligent selection logic as the CV draft generator:

1. **Build TargetSpec** from job description
2. **Select relevant experiences** using `select_experiences()`
3. **Select relevant skills** using `select_skills()`
4. **Select relevant education** using `select_education()`
5. **Format only the selected/filtered data** for the LLM prompt

### Implementation Steps

1. Import selection functions:
   ```python
   from backend.services.ai.selection import (
       select_education,
       select_experiences,
       select_skills,
   )
   from backend.services.ai.target_spec import build_target_spec
   ```

2. Modify `generate_cover_letter()`:
   ```python
   async def generate_cover_letter(
       profile: ProfileData, request: CoverLetterRequest
   ) -> CoverLetterResponse:
       # ... existing LLM check ...

       # Build target spec from job description
       spec = build_target_spec(request.job_description)

       # Select relevant experiences (max 5 for cover letter)
       selected_experiences, _ = select_experiences(
           profile.experience, spec, max_experiences=5
       )

       # Select relevant education
       selected_education = select_education(
           profile.education, spec, max_education=2
       )

       # Select relevant skills
       selected_skills = select_skills(
           profile.skills, spec, selected_experiences
       )

       # Create filtered profile for summary
       filtered_profile = ProfileData(
           personal_info=profile.personal_info,
           experience=selected_experiences,
           education=selected_education,
           skills=selected_skills,
       )

       # Format filtered profile summary
       profile_summary = _format_profile_summary(filtered_profile)

       # ... rest of the function ...
   ```

3. Update `_format_profile_summary()` to work with already-filtered data (remove the slicing since data is pre-filtered):
   ```python
   def _format_profile_summary(profile: ProfileData) -> str:
       """Format profile data into a summary for LLM context."""
       # Remove [:5], [:2], [:3], [:15] slices since data is pre-filtered
       # Keep the formatting logic but use all items in the filtered lists
   ```

### Benefits

- **Relevance**: Only job-relevant experiences/technologies are sent to LLM
- **Consistency**: Same selection logic as CV draft generator
- **Better Results**: LLM focuses on relevant content (Django/Node.js) instead of irrelevant (LAMP)
- **Maintainability**: Single source of truth for selection logic

### Testing Considerations

- Test with profiles containing both relevant and irrelevant technologies
- Verify that relevant technologies (Django, Node.js) are prioritized over irrelevant ones (LAMP)
- Ensure cover letters mention the most relevant experiences first
- Test edge cases: all experiences relevant, all irrelevant, mixed
