"""Main CV generation logic using odfpy."""
import logging
from typing import Dict, Any
from odf.opendocument import OpenDocumentText
from odf.text import P, H, Span, List, ListItem
from odf.table import Table, TableRow, TableCell, TableColumn
from odf.draw import Frame, TextBox
from backend.cv_generator.styles import CVStyles

logger = logging.getLogger(__name__)


class CVGenerator:
    """Generate ODT CV documents."""

    def __init__(self):
        self.styles = CVStyles()

    def generate(self, cv_data: Dict[str, Any], output_path: str) -> str:
        """Generate ODT file from CV data."""
        # Extract and validate theme
        theme = cv_data.get("theme", "classic")
        logger.debug(
            "Generating CV with theme: %s (from cv_data keys: %s)",
            theme,
            list(cv_data.keys()),
        )

        # Create document
        doc = OpenDocumentText()

        # Add styles
        doc = self.styles.create_styles(doc, theme=theme)

        # Get text body
        text_body = doc.text

        personal_info = cv_data.get("personal_info", {})

        # Add header with personal info
        if theme == "accented":
            self._add_accented_header(text_body, personal_info)
        else:
            self._add_header(text_body, personal_info)

        # Add summary if available
        if theme == "accented":
            self._add_accented_body(text_body, cv_data)
        else:
            if personal_info.get("summary"):
                self._add_section(text_body, "Summary", personal_info["summary"])

        # Add experience section
        if theme != "accented" and cv_data.get("experience"):
            self._add_experience_section(text_body, cv_data["experience"])

        # Add education section
        if theme != "accented" and cv_data.get("education"):
            self._add_education_section(text_body, cv_data["education"])

        # Add skills section
        if theme != "accented" and cv_data.get("skills"):
            self._add_skills_section(text_body, cv_data["skills"])

        # Save document
        doc.save(output_path)
        return output_path

    def _format_address(self, address: Dict[str, Any]) -> str:
        """Format address components into a readable string."""
        if not address:
            return ""

        parts = []
        if address.get("street"):
            parts.append(address["street"])
        if address.get("city"):
            parts.append(address["city"])
        if address.get("state"):
            parts.append(address["state"])
        if address.get("zip"):
            parts.append(address["zip"])
        if address.get("country"):
            parts.append(address["country"])

        return ", ".join(parts)

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
        address_str = self._format_address(personal_info.get("address"))
        if address_str:
            contact_info.append(f"Address: {address_str}")
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

    def _add_accented_header(self, text_body, personal_info: Dict[str, Any]):
        """Add accented header with a photo placeholder."""
        topbar = P(stylename="TopBar")
        topbar.addText(" ")
        text_body.addElement(topbar)

        header_table = Table(name="HeaderTable")
        header_table.addElement(TableColumn(stylename="HeaderColLeft"))
        header_table.addElement(TableColumn(stylename="HeaderColRight"))
        header_row = TableRow()
        header_table.addElement(header_row)

        left_cell = TableCell(stylename="HeaderCellLeft")
        right_cell = TableCell(stylename="HeaderCellRight")
        header_row.addElement(left_cell)
        header_row.addElement(right_cell)

        name = personal_info.get("name", "")
        if name:
            name_p = P(stylename="HeaderName")
            name_p.addText(name)
            left_cell.addElement(name_p)

        title = personal_info.get("title", "")
        if title:
            title_p = P(stylename="HeaderTitle")
            title_p.addText(title)
            left_cell.addElement(title_p)

        contact_info = []
        if personal_info.get("email"):
            contact_info.append(f"Email: {personal_info['email']}")
        if personal_info.get("phone"):
            contact_info.append(f"Phone: {personal_info['phone']}")
        address_str = self._format_address(personal_info.get("address"))
        if address_str:
            contact_info.append(f"Address: {address_str}")
        if personal_info.get("linkedin"):
            contact_info.append(f"LinkedIn: {personal_info['linkedin']}")
        if personal_info.get("github"):
            contact_info.append(f"GitHub: {personal_info['github']}")
        if personal_info.get("website"):
            contact_info.append(f"Website: {personal_info['website']}")

        if contact_info:
            contact_p = P(stylename="Normal")
            contact_p.addText(" | ".join(contact_info))
            left_cell.addElement(contact_p)

        frame = Frame(width="4cm", height="4cm", anchortype="paragraph")
        textbox = TextBox()
        photo_p = P(stylename="PhotoText")
        photo_p.addText("Photo")
        textbox.addElement(photo_p)
        frame.addElement(textbox)
        right_cell.addElement(frame)

        text_body.addElement(header_table)

    def _add_accented_body(self, text_body, cv_data: Dict[str, Any]):
        """Add two-column body for the accented layout."""
        body_table = Table(name="BodyTable", stylename="BodyTable")
        body_table.addElement(TableColumn(stylename="MainCol"))
        body_table.addElement(TableColumn(stylename="SideCol"))
        body_row = TableRow()
        body_table.addElement(body_row)

        left_cell = TableCell(stylename="MainCell")
        right_cell = TableCell(stylename="SideCell")
        body_row.addElement(left_cell)
        body_row.addElement(right_cell)

        personal_info = cv_data.get("personal_info", {})
        if personal_info.get("summary"):
            self._add_accented_section(left_cell, "Profile", personal_info["summary"])

        experiences = cv_data.get("experience", [])
        if experiences:
            projects_heading = H(outlinelevel=2, stylename="Subheading")
            projects_heading.addText("Project References")
            left_cell.addElement(projects_heading)
            items = []
            for exp in experiences:
                title = exp.get("title", "")
                company = exp.get("company", "")
                dates = " - ".join(
                    filter(None, [exp.get("start_date"), exp.get("end_date")])
                )
                parts = [part for part in [title, company] if part]
                line = " at ".join(parts) if parts else ""
                if dates:
                    line = f"{line} ({dates})" if line else dates
                if line:
                    items.append(line)
            self._add_bullet_list(left_cell, items)

        skills = cv_data.get("skills", [])
        if skills:
            competencies_heading = H(outlinelevel=2, stylename="Subheading")
            competencies_heading.addText("Core Competencies")
            right_cell.addElement(competencies_heading)
            skills_by_category = {}
            for skill in skills:
                category = skill.get("category", "Other") or "Other"
                skills_by_category.setdefault(category, []).append(
                    skill.get("name", "")
                )
            for category, skill_names in skills_by_category.items():
                category_p = P(stylename="SectionTitle")
                category_p.addText(category)
                right_cell.addElement(category_p)
                self._add_bullet_list(
                    right_cell, [name for name in skill_names if name]
                )

        text_body.addElement(body_table)

    def _add_accented_section(self, container, title: str, content: str):
        h = H(outlinelevel=2, stylename="Subheading")
        h.addText(title)
        container.addElement(h)

        p = P(stylename="Normal")
        p.addText(content)
        container.addElement(p)

    def _add_bullet_list(self, container, items: list):
        if not items:
            return
        lst = List()
        for item in items:
            list_item = ListItem()
            p = P(stylename="BulletText")
            p.addText(item)
            list_item.addElement(p)
            lst.addElement(list_item)
        container.addElement(lst)

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
