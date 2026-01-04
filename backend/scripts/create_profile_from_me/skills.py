"""Skills data."""
from typing import List, Dict, Any


def get_skills_data() -> List[Dict[str, Any]]:
    """Get skills data.

    Returns:
        List of skill dictionaries
    """
    return [
        # Programming Languages
        {"name": "Python", "category": "Programming Languages", "level": "Expert"},
        {
            "name": "TypeScript",
            "category": "Programming Languages",
            "level": "Advanced",
        },
        {
            "name": "JavaScript",
            "category": "Programming Languages",
            "level": "Advanced",
        },
        {"name": "SQL", "category": "Programming Languages", "level": "Advanced"},
        {"name": "PHP", "category": "Programming Languages", "level": "Advanced"},
        # Backend & Application Development
        {"name": "Django", "category": "Backend", "level": "Expert"},
        {"name": "REST API Design", "category": "Backend", "level": "Expert"},
        {"name": "Backend Architecture", "category": "Backend", "level": "Expert"},
        {"name": "Multi-tenant Systems", "category": "Backend", "level": "Expert"},
        {
            "name": "Single-tenant Secure Deployments",
            "category": "Backend",
            "level": "Expert",
        },
        {"name": "Business Logic Modeling", "category": "Backend", "level": "Expert"},
        {"name": "Workflow Automation", "category": "Backend", "level": "Expert"},
        # Frontend Development
        {"name": "React", "category": "Frontend", "level": "Advanced"},
        {"name": "Tailwind CSS", "category": "Frontend", "level": "Advanced"},
        # Databases & Data Modeling
        {"name": "PostgreSQL", "category": "Databases", "level": "Expert"},
        {"name": "Neo4j (Graph DB)", "category": "Databases", "level": "Expert"},
        {
            "name": "Relational Data Modeling",
            "category": "Databases",
            "level": "Expert",
        },
        {
            "name": "Graph-based Data Modeling",
            "category": "Databases",
            "level": "Expert",
        },
        {
            "name": "pgvector / Vector Search",
            "category": "Databases",
            "level": "Advanced",
        },
        {"name": "Redis", "category": "Databases", "level": "Advanced"},
        # AI / Machine Learning
        {
            "name": "LLM Integration (OpenAI / Azure AI)",
            "category": "AI/ML",
            "level": "Expert",
        },
        {
            "name": "AI-assisted Assessment Generation",
            "category": "AI/ML",
            "level": "Expert",
        },
        {
            "name": "AI Evaluation & Scoring Logic",
            "category": "AI/ML",
            "level": "Expert",
        },
        {"name": "Prompt & System Design", "category": "AI/ML", "level": "Expert"},
        {"name": "Policy-aware AI Workflows", "category": "AI/ML", "level": "Advanced"},
        {
            "name": "Embedding & Retrieval (RAG)",
            "category": "AI/ML",
            "level": "Advanced",
        },
        # Security, GRC & Compliance
        {
            "name": "ISO 27001 / ISMS Implementation",
            "category": "Security/GRC",
            "level": "Expert",
        },
        {
            "name": "CIS Controls / CIS18 Operationalization",
            "category": "Security/GRC",
            "level": "Expert",
        },
        {
            "name": "GRC Process Automation",
            "category": "Security/GRC",
            "level": "Expert",
        },
        {
            "name": "Risk Modeling & Assessment",
            "category": "Security/GRC",
            "level": "Expert",
        },
        {
            "name": "CMDB & Asset Dependency Modeling",
            "category": "Security/GRC",
            "level": "Expert",
        },
        {"name": "Gap Analysis", "category": "Security/GRC", "level": "Expert"},
        {
            "name": "Vulnerability Triage & Mitigation Coordination",
            "category": "Security/GRC",
            "level": "Advanced",
        },
        {
            "name": "Audit Support & Reporting",
            "category": "Security/GRC",
            "level": "Advanced",
        },
        # DevOps, Cloud & Infrastructure
        {"name": "DigitalOcean", "category": "DevOps/Cloud", "level": "Advanced"},
        {"name": "CI/CD Pipelines", "category": "DevOps/Cloud", "level": "Advanced"},
        {
            "name": "Infrastructure as Code",
            "category": "DevOps/Cloud",
            "level": "Advanced",
        },
        {
            "name": "Secure System Deployment",
            "category": "DevOps/Cloud",
            "level": "Advanced",
        },
        {
            "name": "Single-tenant Isolation Strategies",
            "category": "DevOps/Cloud",
            "level": "Expert",
        },
        # Integrations & Tooling
        {
            "name": "Atlassian Confluence (Automation & Publishing)",
            "category": "Integrations",
            "level": "Advanced",
        },
        {"name": "Jira Integration", "category": "Integrations", "level": "Advanced"},
        {
            "name": "Microsoft / Azure Ecosystem",
            "category": "Integrations",
            "level": "Advanced",
        },
        {
            "name": "Excel-based Reporting Automation",
            "category": "Integrations",
            "level": "Expert",
        },
        # Architecture & System Design
        {
            "name": "End-to-end System Architecture",
            "category": "Architecture",
            "level": "Expert",
        },
        {
            "name": "Scalable Compliance Platforms",
            "category": "Architecture",
            "level": "Expert",
        },
        {
            "name": "Data-driven KPI Systems",
            "category": "Architecture",
            "level": "Expert",
        },
        {
            "name": "Security-by-design Architecture",
            "category": "Architecture",
            "level": "Expert",
        },
        {
            "name": "Closed-circuit / Local Deployments",
            "category": "Architecture",
            "level": "Expert",
        },
        # Consulting & Professional Skills
        {
            "name": "Client Advisory (CISO / Security Teams)",
            "category": "Consulting",
            "level": "Advanced",
        },
        {
            "name": "Requirements Translation (Business → System)",
            "category": "Consulting",
            "level": "Expert",
        },
        {"name": "Technical Leadership", "category": "Consulting", "level": "Expert"},
        {
            "name": "Product Vision & Roadmap Ownership",
            "category": "Consulting",
            "level": "Expert",
        },
        {
            "name": "Independent Delivery & Accountability",
            "category": "Consulting",
            "level": "Expert",
        },
    ]
