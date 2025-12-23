"""DOCX CV generation pipeline."""
from backend.cv_generator_docx.generator import DocxCVGenerator
from backend.cv_generator_docx.template_builder import ensure_template

__all__ = ["DocxCVGenerator", "ensure_template"]
