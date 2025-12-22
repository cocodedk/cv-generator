"""Main CV generation logic using odfpy."""
from typing import Dict, Any
from datetime import datetime
from odf.opendocument import OpenDocumentText
from odf.text import P, H, Span
from odf.style import Style
from backend.cv_generator.styles import CVStyles


class CVGenerator:
    """Generate ODT CV documents."""

    def __init__(self):
        self.styles = CVStyles()

    def generate(self, cv_data: Dict[str, Any], output_path: str) -> str:
        """Generate ODT file from CV data."""
        # Create document
        doc = OpenDocumentText()

        # Add styles
        doc = self.styles.create_styles(doc)

        # Get text body
        text_body = doc.text

        # Add header with personal info
        self._add_header(text_body, cv_data.get("personal_info", {}))

        # Add summary if available
        if cv_data.get("personal_info", {}).get("summary"):
            self._add_section(text_body, "Summary", cv_data["personal_info"]["summary"])

        # Add experience section
        if cv_data.get("experience"):
            self._add_experience_section(text_body, cv_data["experience"])

        # Add education section
        if cv_data.get("education"):
            self._add_education_section(text_body, cv_data["education"])

        # Add skills section
        if cv_data.get("skills"):
            self._add_skills_section(text_body, cv_data["skills"])

        # Save document
        doc.save(output_path)
        return output_path

    def _add_header(self, text_body, personal_info: Dict[str, Any]):
        """Add CV header with personal information."""
        name = personal_info.get("name", "")
        if name:
            h = H(outlinelevel=1, stylename="Heading")
            h.addText(name)
            text_body.addElement(h)

        # Contact information
        contact_info = []
        if personal_info.get("email"):
            contact_info.append(f"Email: {personal_info['email']}")
        if personal_info.get("phone"):
            contact_info.append(f"Phone: {personal_info['phone']}")
        if personal_info.get("address"):
            contact_info.append(f"Address: {personal_info['address']}")
        if personal_info.get("linkedin"):
            contact_info.append(f"LinkedIn: {personal_info['linkedin']}")
        if personal_info.get("github"):
            contact_info.append(f"GitHub: {personal_info['github']}")
        if personal_info.get("website"):
            contact_info.append(f"Website: {personal_info['website']}")

        if contact_info:
            p = P(stylename="Normal")
            p.addText(" | ".join(contact_info))
            text_body.addElement(p)

    def _add_section(self, text_body, title: str, content: str):
        """Add a section with title and content."""
        h = H(outlinelevel=2, stylename="Subheading")
        h.addText(title)
        text_body.addElement(h)

        p = P(stylename="Normal")
        p.addText(content)
        text_body.addElement(p)

    def _add_experience_section(self, text_body, experiences: list):
        """Add work experience section."""
        h = H(outlinelevel=2, stylename="Subheading")
        h.addText("Experience")
        text_body.addElement(h)

        for exp in experiences:
            # Job title and company
            p = P(stylename="SectionTitle")
            title_span = Span(stylename="Emphasis")
            title_span.addText(exp.get("title", ""))
            p.addElement(title_span)
            p.addText(f" at {exp.get('company', '')}")
            text_body.addElement(p)

            # Dates and location
            date_info = []
            if exp.get("start_date"):
                date_info.append(exp["start_date"])
            if exp.get("end_date"):
                date_info.append(exp["end_date"])

            if date_info:
                p = P(stylename="Normal")
                p.addText(" | ".join(date_info))
                if exp.get("location"):
                    p.addText(f" | {exp['location']}")
                text_body.addElement(p)

            # Description
            if exp.get("description"):
                p = P(stylename="Normal")
                p.addText(exp["description"])
                text_body.addElement(p)

    def _add_education_section(self, text_body, educations: list):
        """Add education section."""
        h = H(outlinelevel=2, stylename="Subheading")
        h.addText("Education")
        text_body.addElement(h)

        for edu in educations:
            p = P(stylename="SectionTitle")
            degree_span = Span(stylename="Emphasis")
            degree_span.addText(edu.get("degree", ""))
            p.addElement(degree_span)
            p.addText(f", {edu.get('institution', '')}")
            text_body.addElement(p)

            edu_info = []
            if edu.get("year"):
                edu_info.append(edu["year"])
            if edu.get("field"):
                edu_info.append(edu["field"])
            if edu.get("gpa"):
                edu_info.append(f"GPA: {edu['gpa']}")

            if edu_info:
                p = P(stylename="Normal")
                p.addText(" | ".join(edu_info))
                text_body.addElement(p)

    def _add_skills_section(self, text_body, skills: list):
        """Add skills section."""
        h = H(outlinelevel=2, stylename="Subheading")
        h.addText("Skills")
        text_body.addElement(h)

        # Group skills by category if available
        skills_by_category = {}
        uncategorized = []

        for skill in skills:
            category = skill.get("category", "Other")
            if category:
                if category not in skills_by_category:
                    skills_by_category[category] = []
                skills_by_category[category].append(skill.get("name", ""))
            else:
                uncategorized.append(skill.get("name", ""))

        # Add categorized skills
        for category, skill_names in skills_by_category.items():
            p = P(stylename="SectionTitle")
            p.addText(f"{category}: ")
            p.addText(", ".join(skill_names))
            text_body.addElement(p)

        # Add uncategorized skills
        if uncategorized:
            p = P(stylename="Normal")
            p.addText(", ".join(uncategorized))
            text_body.addElement(p)
