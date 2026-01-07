"""Technology term extraction utilities."""

import re
from typing import Set

from backend.services.ai.text import extract_words

# Pattern to extract tech from parentheses like (e.g., Terraform) or (e.g. Docker, Kubernetes)
_TECH_IN_PARENS_PATTERN = re.compile(r'\((?:e\.?g\.?[,:]?\s*)([^)]+)\)', re.IGNORECASE)

# Known multi-word technology names (lowercase for matching)
_KNOWN_MULTI_WORD_TECH = frozenset({
    "github actions", "azure devops", "azure openai", "azure functions",
    "google cloud", "google cloud platform", "amazon web services",
    "infrastructure as code", "ci/cd", "ci cd",
    "machine learning", "deep learning", "natural language processing",
    "rest api", "rest apis", "graphql api",
    "visual studio", "visual studio code", "vs code",
    "sql server", "ms sql", "microsoft sql server",
    "power bi", "azure data factory", "azure synapse",
    "amazon s3", "amazon ec2", "amazon rds", "amazon lambda",
    "google kubernetes engine", "amazon eks", "azure aks",
    "spring boot", "ruby on rails", "react native",
    "node.js", "next.js", "vue.js", "nuxt.js", "express.js",
    "asp.net", ".net core", ".net framework",
})

_REQUIRED_HINTS = ("must", "required", "requirement", "you will", "we need", "essential")
_PREFERRED_HINTS = ("nice to have", "plus", "bonus", "preferred", "desirable")
_SENIORITY_SIGNALS = ("senior", "lead", "principal", "architect", "manager", "director", "junior", "mid", "entry")

# Stopwords to filter out when extracting skills from JD
_STOPWORDS = frozenset({
    # Common verbs
    "experience", "working", "writing", "building", "developing", "understanding",
    "creating", "designing", "maintaining", "improving", "delivering", "using",
    "managing", "leading", "collaborating", "communicating", "analyzing",
    # Common nouns
    "years", "year", "team", "teams", "environment", "environments", "code",
    "software", "application", "applications", "system", "systems", "solution",
    "solutions", "project", "projects", "product", "products", "service", "services",
    # Prepositions and articles
    "in", "on", "at", "to", "for", "with", "from", "by", "of", "the", "a", "an",
    # Pronouns and determiners
    "we", "you", "our", "your", "their", "this", "that", "these", "those",
    # Conjunctions
    "and", "or", "but", "if", "as", "while", "when", "where", "how", "what",
    # Adjectives
    "fluent", "strong", "good", "excellent", "deep", "solid", "proven", "relevant",
    # Misc common words
    "ability", "skills", "knowledge", "stack", "technology", "technologies",
    "tools", "data", "based", "driven", "oriented", "focused", "related",
    "etc", "e.g", "i.e", "including", "such", "like", "similar",
    # Short words that are rarely tech terms
    "is", "are", "be", "have", "has", "had", "do", "does", "did", "will", "can",
    "should", "would", "could", "may", "might", "shall",
})

# Known single-word tech terms (to prioritize over generic words)
_KNOWN_TECH_TERMS = frozenset({
    # Cloud providers
    "aws", "azure", "gcp", "heroku", "digitalocean", "cloudflare",
    # Languages
    "python", "java", "javascript", "typescript", "golang", "go", "rust", "ruby",
    "scala", "kotlin", "swift", "php", "perl", "bash", "powershell", "sql", "r",
    "c", "c++", "c#", "csharp", "objective-c", "matlab", "julia", "elixir", "erlang",
    # Databases
    "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "sqlite", "oracle", "mariadb", "neo4j", "couchdb",
    # Frameworks/Libraries
    "django", "flask", "fastapi", "react", "angular", "vue", "svelte", "nextjs",
    "express", "nestjs", "spring", "rails", "laravel", "symfony",
    # DevOps/Infrastructure
    "docker", "kubernetes", "k8s", "terraform", "ansible", "puppet", "chef",
    "jenkins", "circleci", "travisci", "gitlab", "github", "bitbucket",
    "prometheus", "grafana", "datadog", "splunk", "elk", "nginx", "apache",
    # Data/ML
    "pandas", "numpy", "scipy", "tensorflow", "pytorch", "keras", "scikit-learn",
    "spark", "hadoop", "kafka", "airflow", "dbt", "snowflake", "databricks",
    # Other tools
    "git", "jira", "confluence", "slack", "figma", "postman", "swagger",
    "graphql", "grpc", "rabbitmq", "celery", "redis", "memcached",
})


def _extract_tech_terms(text: str) -> Set[str]:
    """
    Extract technology terms from text using smart patterns.

    Handles:
    - Tech in parentheses: (e.g., Terraform, Docker)
    - Known multi-word tech: GitHub Actions, Azure DevOps
    - Known single-word tech: Python, AWS, Docker
    - Comma-separated lists in parentheses
    """
    extracted: Set[str] = set()
    text_lower = text.lower()

    # 1. Extract from parentheses patterns like (e.g., Terraform) or (e.g. Docker, Kubernetes)
    for match in _TECH_IN_PARENS_PATTERN.finditer(text):
        content = match.group(1)
        # Split by comma and clean up
        for item in content.split(","):
            item = item.strip().strip(".")
            if item and len(item) >= 2:
                # Preserve original case for tech terms
                extracted.add(item)

    # 2. Find known multi-word tech terms
    for tech in _KNOWN_MULTI_WORD_TECH:
        if tech in text_lower:
            extracted.add(tech)

    # 3. Find known single-word tech terms (case-insensitive)
    words = set(extract_words(text))
    for word in words:
        # Strip trailing punctuation for matching
        word_clean = word.rstrip(".,;:!?")
        if word_clean in _KNOWN_TECH_TERMS:
            extracted.add(word_clean)

    return extracted
