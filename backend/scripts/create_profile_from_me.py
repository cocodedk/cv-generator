"""Create profile automatically from docs/me.md data.

This script creates a profile in the Neo4j database using data extracted from docs/me.md.
It includes personal information, work experience, education, and skills.

Usage:
    docker-compose exec app python backend/scripts/create_profile_from_me.py

The script will:
    1. Create a Profile node in Neo4j
    2. Create Person node with personal information
    3. Create Experience nodes with projects
    4. Create Education nodes
    5. Create Skill nodes with categories and levels

If a profile already exists, it will be updated with the new data.
"""
import sys

# Add app directory to path (Docker container has /app as working directory)
sys.path.insert(0, '/app')

from backend.database.queries.profile import save_profile


def create_profile_from_me_data():
    """Create profile using data from docs/me.md."""

    # Parse address from: "Magistervej 54 3. th, 2400 Copenhagen NV"
    # Street: "Magistervej 54 3. th"
    # City: "Copenhagen NV"
    # Zip: "2400"
    # Country: "Denmark"

    profile_data = {
        "personal_info": {
            "name": "Babak Bandpey",
            "title": "Senior Freelance Software Engineer / Security & GRC Specialist",
            "email": "babak@cocode.dk",
            "phone": "+45 27 82 30 77",
            "address": {
                "street": "Magistervej 54 3. th",
                "city": "Copenhagen NV",
                "zip": "2400",
                "country": "Denmark"
            },
            "linkedin": "https://www.linkedin.com/in/babakbandpey/",
            "github": "https://github.com/cocodedk",
            "website": "https://cocode.dk",
            "summary": (
                "Senior systems architect who operationalizes security, compliance, and AI "
                "into measurable business outcomes. Conceived, architected, and built FITS, "
                "a production-grade AI-driven GRC platform used by real organizations. "
                "Expert in Python, Django, PostgreSQL, Neo4j, React, and AI/LLM integration. "
                "Hands-on experience with ISO 27001, CIS Controls, ISMS implementation, "
                "and large-scale compliance automation."
            )
        },
        "experience": [
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
        ],
        "education": [
            {
                "degree": "Datamatiker",
                "institution": "Niels Brock Copenhagen Business College",
                "field": "Computer Science",
                "year": "2000"
            },
            {
                "degree": "Advanced Diploma / Continuing Education in Cybersecurity",
                "institution": "Erhvervsakademi / EK",
                "field": "Cybersecurity and Information Security Management",
                "year": "2020"
            }
        ],
        "skills": [
            # Programming Languages
            {"name": "Python", "category": "Programming Languages", "level": "Expert"},
            {"name": "TypeScript", "category": "Programming Languages", "level": "Advanced"},
            {"name": "JavaScript", "category": "Programming Languages", "level": "Advanced"},
            {"name": "SQL", "category": "Programming Languages", "level": "Advanced"},
            {"name": "PHP", "category": "Programming Languages", "level": "Advanced"},

            # Backend & Application Development
            {"name": "Django", "category": "Backend", "level": "Expert"},
            {"name": "REST API Design", "category": "Backend", "level": "Expert"},
            {"name": "Backend Architecture", "category": "Backend", "level": "Expert"},
            {"name": "Multi-tenant Systems", "category": "Backend", "level": "Expert"},
            {"name": "Single-tenant Secure Deployments", "category": "Backend", "level": "Expert"},
            {"name": "Business Logic Modeling", "category": "Backend", "level": "Expert"},
            {"name": "Workflow Automation", "category": "Backend", "level": "Expert"},

            # Frontend Development
            {"name": "React", "category": "Frontend", "level": "Advanced"},
            {"name": "Tailwind CSS", "category": "Frontend", "level": "Advanced"},

            # Databases & Data Modeling
            {"name": "PostgreSQL", "category": "Databases", "level": "Expert"},
            {"name": "Neo4j (Graph DB)", "category": "Databases", "level": "Expert"},
            {"name": "Relational Data Modeling", "category": "Databases", "level": "Expert"},
            {"name": "Graph-based Data Modeling", "category": "Databases", "level": "Expert"},
            {"name": "pgvector / Vector Search", "category": "Databases", "level": "Advanced"},
            {"name": "Redis", "category": "Databases", "level": "Advanced"},

            # AI / Machine Learning
            {"name": "LLM Integration (OpenAI / Azure AI)", "category": "AI/ML", "level": "Expert"},
            {"name": "AI-assisted Assessment Generation", "category": "AI/ML", "level": "Expert"},
            {"name": "AI Evaluation & Scoring Logic", "category": "AI/ML", "level": "Expert"},
            {"name": "Prompt & System Design", "category": "AI/ML", "level": "Expert"},
            {"name": "Policy-aware AI Workflows", "category": "AI/ML", "level": "Advanced"},
            {"name": "Embedding & Retrieval (RAG)", "category": "AI/ML", "level": "Advanced"},

            # Security, GRC & Compliance
            {"name": "ISO 27001 / ISMS Implementation", "category": "Security/GRC", "level": "Expert"},
            {"name": "CIS Controls / CIS18 Operationalization", "category": "Security/GRC", "level": "Expert"},
            {"name": "GRC Process Automation", "category": "Security/GRC", "level": "Expert"},
            {"name": "Risk Modeling & Assessment", "category": "Security/GRC", "level": "Expert"},
            {"name": "CMDB & Asset Dependency Modeling", "category": "Security/GRC", "level": "Expert"},
            {"name": "Gap Analysis", "category": "Security/GRC", "level": "Expert"},
            {"name": "Vulnerability Triage & Mitigation Coordination", "category": "Security/GRC", "level": "Advanced"},
            {"name": "Audit Support & Reporting", "category": "Security/GRC", "level": "Advanced"},

            # DevOps, Cloud & Infrastructure
            {"name": "DigitalOcean", "category": "DevOps/Cloud", "level": "Advanced"},
            {"name": "CI/CD Pipelines", "category": "DevOps/Cloud", "level": "Advanced"},
            {"name": "Infrastructure as Code", "category": "DevOps/Cloud", "level": "Advanced"},
            {"name": "Secure System Deployment", "category": "DevOps/Cloud", "level": "Advanced"},
            {"name": "Single-tenant Isolation Strategies", "category": "DevOps/Cloud", "level": "Expert"},

            # Integrations & Tooling
            {"name": "Atlassian Confluence (Automation & Publishing)", "category": "Integrations", "level": "Advanced"},
            {"name": "Jira Integration", "category": "Integrations", "level": "Advanced"},
            {"name": "Microsoft / Azure Ecosystem", "category": "Integrations", "level": "Advanced"},
            {"name": "Excel-based Reporting Automation", "category": "Integrations", "level": "Expert"},

            # Architecture & System Design
            {"name": "End-to-end System Architecture", "category": "Architecture", "level": "Expert"},
            {"name": "Scalable Compliance Platforms", "category": "Architecture", "level": "Expert"},
            {"name": "Data-driven KPI Systems", "category": "Architecture", "level": "Expert"},
            {"name": "Security-by-design Architecture", "category": "Architecture", "level": "Expert"},
            {"name": "Closed-circuit / Local Deployments", "category": "Architecture", "level": "Expert"},

            # Consulting & Professional Skills
            {"name": "Client Advisory (CISO / Security Teams)", "category": "Consulting", "level": "Advanced"},
            {"name": "Requirements Translation (Business → System)", "category": "Consulting", "level": "Expert"},
            {"name": "Technical Leadership", "category": "Consulting", "level": "Expert"},
            {"name": "Product Vision & Roadmap Ownership", "category": "Consulting", "level": "Expert"},
            {"name": "Independent Delivery & Accountability", "category": "Consulting", "level": "Expert"}
        ]
    }

    try:
        print("Creating profile from docs/me.md data...")
        result = save_profile(profile_data)

        if result:
            print("✅ Profile created successfully!")
            print(f"   Name: {profile_data['personal_info']['name']}")
            print(f"   Email: {profile_data['personal_info']['email']}")
            print(f"   Experiences: {len(profile_data['experience'])}")
            print(f"   Education: {len(profile_data['education'])}")
            print(f"   Skills: {len(profile_data['skills'])}")
            return True
        else:
            print("❌ Failed to create profile")
            return False

    except Exception as e:
        print(f"❌ Error creating profile: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = create_profile_from_me_data()
        sys.exit(0 if success else 1)
    finally:
        from backend.database.connection import Neo4jConnection
        Neo4jConnection.close()
