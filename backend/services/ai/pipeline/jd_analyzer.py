"""Step 1: Analyze job description to extract structured requirements."""

import logging
import re
from typing import Set, List
from backend.services.ai.pipeline.models import JDAnalysis
from backend.services.ai.llm_client import get_llm_client
from backend.services.ai.text import extract_words, normalize_text

logger = logging.getLogger(__name__)

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


async def analyze_jd(job_description: str) -> JDAnalysis:
    """
    Analyze job description to extract structured requirements.

    Uses LLM if available for better understanding, falls back to heuristics.

    Args:
        job_description: The job description text

    Returns:
        JDAnalysis with extracted requirements
    """
    logger.info(f"Analyzing JD ({len(job_description)} chars)")
    llm_client = get_llm_client()

    if llm_client.is_configured():
        try:
            result = await _analyze_with_llm(llm_client, job_description)
            logger.info(
                f"JD Analysis result: {len(result.required_skills)} required, "
                f"{len(result.preferred_skills)} preferred, {len(result.responsibilities)} responsibilities"
            )
            return result
        except Exception as e:
            logger.warning(f"LLM analysis failed, falling back to heuristics: {e}")

    # Fallback to heuristics when LLM not configured or fails
    logger.info("Using heuristic JD analysis (LLM not available)")
    result = _analyze_with_heuristics(job_description)
    logger.info(
        f"JD Analysis result (heuristics): {len(result.required_skills)} required, "
        f"{len(result.preferred_skills)} preferred, {len(result.responsibilities)} responsibilities"
    )
    return result


async def _analyze_with_llm(llm_client, job_description: str) -> JDAnalysis:
    """Use LLM to extract structured requirements."""
    prompt = f"""Analyze this job description and extract structured requirements.

Job Description:
{job_description[:3000]}

Extract and categorize:
1. Required skills/technologies (must-have)
2. Preferred skills/technologies (nice-to-have)
3. Key responsibilities/duties
4. Domain/industry keywords
5. Seniority level indicators

Return ONLY a JSON object with this structure:
{{
  "required_skills": ["skill1", "skill2", ...],
  "preferred_skills": ["skill1", "skill2", ...],
  "responsibilities": ["duty1", "duty2", ...],
  "domain_keywords": ["keyword1", "keyword2", ...],
  "seniority_signals": ["senior", "lead", ...]
}}

Be specific with technology names (e.g., "Node.js", "React", "PostgreSQL").
Include frameworks, languages, tools, and methodologies mentioned."""

    try:
        response = await llm_client.rewrite_text("", prompt)
        # Parse JSON from response
        import json

        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return JDAnalysis(
                    required_skills=set(data.get("required_skills", [])),
                    preferred_skills=set(data.get("preferred_skills", [])),
                    responsibilities=data.get("responsibilities", [])[:10],
                    domain_keywords=set(data.get("domain_keywords", [])),
                    seniority_signals=data.get("seniority_signals", [])[:5],
                )
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM JSON response: {e}, response: {response[:200]}")
                raise
    except Exception as e:
        logger.error(f"LLM JD analysis failed: {e}")
        raise

    # Fallback if parsing fails
    return _analyze_with_heuristics(job_description)


def _analyze_with_heuristics(job_description: str) -> JDAnalysis:
    """Fallback heuristic analysis when LLM is not available."""
    lines = [normalize_text(line) for line in job_description.splitlines() if line.strip()]

    # First, extract tech terms using smart extraction from full JD
    all_tech_terms = _extract_tech_terms(job_description)

    required: Set[str] = set()
    preferred: Set[str] = set()
    responsibilities: List[str] = []
    seniority_signals: List[str] = []

    # Track which section we're in based on hints
    in_preferred_section = False

    for line in lines:
        line_tech = _extract_tech_terms(line)

        # Check for section markers
        if any(hint in line for hint in _PREFERRED_HINTS):
            in_preferred_section = True

        # Check for required skills (explicit markers)
        if any(hint in line for hint in _REQUIRED_HINTS):
            required.update(line_tech)
            in_preferred_section = False

        # Check for preferred skills (explicit markers or in preferred section)
        elif any(hint in line for hint in _PREFERRED_HINTS) or in_preferred_section:
            preferred.update(line_tech)
        else:
            # Default: add to required if not in preferred section
            required.update(line_tech)

        # Extract responsibilities
        if any(verb in line for verb in ("build", "design", "own", "lead", "deliver", "maintain", "improve", "develop", "create")):
            responsibilities.append(line[:140])

        # Check for seniority signals
        for signal in _SENIORITY_SIGNALS:
            if signal in line:
                seniority_signals.append(signal)

    # If nothing extracted from line-by-line, use all tech terms from full JD
    if not required and not preferred:
        required = all_tech_terms

    # Always add all extracted tech terms to ensure nothing is missed
    # Tech terms not already in required/preferred go to domain_keywords
    domain_keywords = all_tech_terms - required - preferred

    return JDAnalysis(
        required_skills=required,
        preferred_skills=preferred,
        responsibilities=responsibilities[:10],
        domain_keywords=domain_keywords,
        seniority_signals=list(set(seniority_signals))[:5],
    )
