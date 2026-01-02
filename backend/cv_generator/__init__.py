"""CV generation pipeline."""
from backend.cv_generator.generator import DocxCVGenerator
from backend.cv_generator.template_builder import ensure_template

__all__ = ["DocxCVGenerator", "ensure_template"]
