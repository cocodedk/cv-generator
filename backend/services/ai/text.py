"""Text helpers for AI heuristics."""

import re
from typing import Iterable, List, Set


_WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9.+#/-]*")
_CAMEL_SPLIT_RE = re.compile(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")


def normalize_text(value: str) -> str:
    return value.lower().strip()


def extract_words(text: str) -> List[str]:
    return [normalize_text(word) for word in _WORD_RE.findall(text)]


def word_set(parts: Iterable[str]) -> Set[str]:
    words: Set[str] = set()
    for part in parts:
        words.update(extract_words(part))
    return words


def contains_any(text: str, needles: Iterable[str]) -> bool:
    lowered = normalize_text(text)
    return any(needle in lowered for needle in needles)


def split_compound(text: str) -> List[str]:
    """Split compound tech names like TailwindCSS → ['tailwind', 'css']."""
    # First split by camelCase/PascalCase
    parts = _CAMEL_SPLIT_RE.split(text)
    # Then normalize each part
    result = []
    for part in parts:
        normalized = normalize_text(part)
        if normalized and len(normalized) >= 2:
            result.append(normalized)
    return result


_TECH_SUFFIXES = {"js", "css", "sql", "api", "db", "ui"}

# Generic words that should not trigger a match on their own in multi-word terms
# These are common business/tech terms that appear in many contexts and don't
# indicate a specific technology match when found alone
_GENERIC_TECH_WORDS = {
    # Cloud providers (too generic without specific service)
    "cloud", "azure", "aws", "google", "microsoft", "openai", "amazon",
    # Common tech concepts
    "security", "design", "architecture", "data", "platform", "system",
    "infrastructure", "development", "integration", "implementation",
    "management", "compliance", "documentation", "specification",
    # Business/process terms
    "leadership", "consulting", "delivery", "frameworks", "methodology",
    "process", "processes", "workflow", "workflows", "governance",
    "strategy", "planning", "execution", "operations", "operations",
    # Team/org terms
    "teams", "team", "organization", "organizational", "stakeholder",
    "stakeholders", "client", "clients", "customer", "customers",
    # Generic action/quality words
    "technical", "professional", "independent", "accountability",
    "responsibility", "responsibilities", "expertise", "experience",
    "skills", "knowledge", "understanding", "proficiency",
    # Common adjectives/adverbs
    "scalable", "reliable", "efficient", "effective", "robust",
    "secure", "modern", "advanced", "enterprise", "production",
    # Project/domain terms
    "project", "projects", "program", "programs", "initiative",
    "initiatives", "solution", "solutions", "service", "services",
    # Testing/quality terms
    "testing", "quality", "assurance", "validation", "verification",
    # Deployment/ops terms
    "deployment", "deployments", "monitoring", "maintenance",
    "support", "administration", "automation", "orchestration",
}


def _strip_tech_suffix(term: str) -> str:
    """Strip common tech suffixes like JS, CSS from a term."""
    lower = term.lower()
    for suffix in _TECH_SUFFIXES:
        if lower.endswith(suffix) and len(lower) > len(suffix) + 2:
            return lower[: -len(suffix)]
    # Handle .js, .ts, .py endings
    for ext in (".js", ".ts", ".py"):
        if lower.endswith(ext):
            return lower[: -len(ext)]
    return lower


def _cores_match_as_prefix(core1: str, core2: str, min_length: int) -> bool:
    """Check if cores match as prefix with short suffix (<=2 chars)."""
    shorter, longer = (core1, core2) if len(core1) <= len(core2) else (core2, core1)
    suffix_len = len(longer) - len(shorter)
    return len(shorter) >= min_length and longer.startswith(shorter) and suffix_len <= 2


def _multiword_match(t1: str, t2: str, core1: str, core2: str, min_len: int) -> bool:
    """Check if multi-word terms match via word cores.

    Requires at least one non-generic word match to avoid false positives
    like "Technical Leadership" matching "Technical documentation".
    """
    words1 = {_strip_tech_suffix(w) for w in t1.split() if len(w) >= min_len}
    words2 = {_strip_tech_suffix(w) for w in t2.split() if len(w) >= min_len}
    words1 = words1 or {core1}
    words2 = words2 or {core2}

    # Find all matching words (non-generic only)
    non_generic_matches = []
    for w1 in words1:
        if len(w1) >= min_len and (w1 == core2 or w1 in words2):
            if w1 not in _GENERIC_TECH_WORDS:
                non_generic_matches.append(w1)

    for w2 in words2:
        if len(w2) >= min_len and (w2 == core1 or w2 in words1):
            if w2 not in _GENERIC_TECH_WORDS and w2 not in non_generic_matches:
                non_generic_matches.append(w2)

    # Only match if we have at least one non-generic word match
    return len(non_generic_matches) > 0


def tech_terms_match(term1: str, term2: str, min_length: int = 3) -> bool:
    """
    Check if two tech terms match, handling compound names.

    Examples:
        - "Tailwind" matches "TailwindCSS"
        - "Tailwind CSS" matches "TailwindCSS"
        - "Next.js" matches "NextJS"
        - "Vue" matches "VueJS"
        - "Java" does NOT match "JavaScript" (different technologies)
    """
    t1 = normalize_text(term1)
    t2 = normalize_text(term2)

    if t1 == t2:
        return True
    if len(t1) < 2 or len(t2) < 2:
        return False

    core1 = _strip_tech_suffix(t1)
    core2 = _strip_tech_suffix(t2)

    if core1 == core2 and len(core1) >= min_length:
        return True
    if _cores_match_as_prefix(core1, core2, min_length):
        return True
    if " " in t1 or " " in t2:
        return _multiword_match(t1, t2, core1, core2, min_length)

    return False
