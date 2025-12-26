"""Experience data."""
from typing import List, Dict, Any


def get_experience_data() -> List[Dict[str, Any]]:
    """Get experience data.

    Returns:
        List of experience dictionaries
    """
    return [
        {
            "title": "Senior Freelance Software Engineer / Security & GRC Specialist",
            "company": "cocode.dk",
            "start_date": "2018-01",
            "end_date": "Present",
            "location": "Copenhagen, Denmark",
            "description": (
                "Independent consultancy providing senior software engineering and security "
                "expertise. Focus on outcome-driven delivery with heavy personal ownership."
            ),
            "projects": [
                {
                    "name": "FITS - AI-Driven GRC Platform",
                    "description": (
                        "Production-grade GRC / security program management platform "
                        "used by real organizations. Functions as GRC automation engine, "
                        "CMDB-like system, and assessment/reporting factory."
                    ),
                    "technologies": [
                        "Python", "Django", "PostgreSQL", "Neo4j", "Redis",
                        "TypeScript", "React", "Tailwind", "pgvector",
                        "OpenAI / Azure AI", "Atlassian Confluence", "Jira"
                    ],
                    "highlights": [
                        "AI-generated security questionnaires",
                        "Policy-aware evaluation of answers",
                        "Automated scoring and assessments",
                        "KPI-rich reporting for CISOs, auditors, and executives",
                        "Reduced assessment turnaround from ~3 weeks to < 48 hours",
                        "Reduced manual review effort by ~75%",
                        "Multi-tenant architecture, operated as single-tenant per customer",
                        "Strong data isolation and compliance alignment"
                    ]
                }
            ]
        },
        {
            "title": "Security & GRC Consultant",
            "company": "L7 Consulting",
            "start_date": "2020-01",
            "end_date": "2024-12",
            "location": "Copenhagen, Denmark",
            "description": (
                "Long-term engagement with high trust and high autonomy. "
                "Built FITS during this period. Focus on GRC automation, "
                "ISMS implementation, and security program management."
            )
        },
        {
            "title": "Security & Compliance Consultant - Phoenix Project",
            "company": "GlobalConnect",
            "start_date": "2022-01",
            "end_date": "2023-12",
            "location": "Copenhagen, Denmark",
            "description": (
                "Participated in large-scale, multi-year initiative to raise cybersecurity "
                "and compliance maturity across complex telecom environment. "
                "Worked with ISO 27001-aligned security controls and ISMS processes. "
                "Translated high-level security policies into concrete, traceable controls. "
                "Conducted security assessments and gap analyses. "
                "Supported vulnerability management and mitigation coordination. "
                "Worked with asset inventories, dependency mapping, and risk classification."
            )
        },
        {
            "title": "GRC Consultant",
            "company": "Nuuday / Danish Telcos",
            "start_date": "2021-01",
            "end_date": "2022-12",
            "location": "Copenhagen, Denmark",
            "description": (
                "Archer-related work in large-scale compliance and security environments. "
                "Worked extensively with RSA Archer as central GRC platform for risk, "
                "control, and assessment management."
            )
        }
    ]
