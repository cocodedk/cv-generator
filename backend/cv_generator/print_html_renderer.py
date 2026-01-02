"""Render CV data into print-friendly A4 HTML."""

import base64
import logging
import mimetypes
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from backend.cv_generator.html_renderer import _prepare_template_data
from backend.cv_generator.layouts import validate_layout
from backend.cv_generator.scramble import scramble_personal_info
from backend.themes import get_theme

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates" / "print_html"
LAYOUTS_DIR = Path(__file__).resolve().parent / "templates" / "layouts"


def render_print_html(cv_data: Dict[str, Any], scramble_config: Dict[str, Any] | None = None) -> str:
    """Render CV data into HTML designed for browser print (A4)."""
    # Prepare template data first to get theme and layout
    template_data = _prepare_template_data(cv_data)
    theme_name = template_data.get("theme", "classic")
    layout_name = template_data.get("layout", "classic-two-column")
    scramble_enabled = bool(scramble_config and scramble_config.get("enabled"))
    scramble_key = scramble_config.get("key") if scramble_config else None

    if scramble_enabled and scramble_key:
        template_data["personal_info"] = scramble_personal_info(
            template_data.get("personal_info", {}),
            scramble_key,
        )
        template_data["scramble_enabled"] = True

    logger.debug(
        "[render_print_html] Input layout from cv_data: %s, from template_data: %s",
        cv_data.get("layout"),
        layout_name,
    )

    # Validate layout name
    layout_name = validate_layout(layout_name)

    # Check for layout-specific template in layouts directory
    layout_template_path = LAYOUTS_DIR / f"{layout_name}.html"

    logger.debug(
        "[render_print_html] Validated layout: %s, template path exists: %s",
        layout_name,
        layout_template_path.exists(),
    )

    # Determine which template to use
    if layout_template_path.exists():
        # Use layout template from layouts directory
        template_dir = LAYOUTS_DIR
        template_name = f"{layout_name}.html"
    else:
        # Fall back to theme-specific template in print_html directory
        theme_template_path = TEMPLATES_DIR / f"{theme_name}.html"
        if theme_template_path.exists():
            template_dir = TEMPLATES_DIR
            template_name = f"{theme_name}.html"
        else:
            # Final fallback to base.html
            template_dir = TEMPLATES_DIR
            template_name = "base.html"

    logger.info(
        "[render_print_html] Using template: %s from dir: %s",
        template_name,
        template_dir,
    )

    # Get theme definition for CSS variables
    theme = get_theme(theme_name)
    accent_color = theme.get("accent_color", theme.get("accent", "#0f766e"))
    section_color = theme.get("section", {}).get("color", accent_color)
    text_color = theme.get("normal", {}).get("color", "#0f172a")
    muted_color = theme.get("text_secondary", "#475569")

    # Add theme CSS variables to template data (will override :root variables)
    template_data["theme_css"] = _build_theme_css(
        accent=accent_color,
        accent_2=section_color,
        ink=text_color,
        muted=muted_color,
    )

    # Create environment with template directory for includes
    # Use both directories so layouts can include components
    env = Environment(
        loader=FileSystemLoader([str(template_dir), str(LAYOUTS_DIR)]),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template(template_name)

    personal_info = template_data.get("personal_info", {})
    photo = personal_info.get("photo")
    if isinstance(photo, str):
        personal_info["photo"] = _maybe_inline_image(photo)

    html = template.render(**template_data)
    if scramble_enabled and scramble_key:
        html = _inject_scramble_script(html)
    return html


def _build_theme_css(accent: str, accent_2: str, ink: str, muted: str) -> str:
    """Build CSS override for theme colors."""
    # Return CSS that will override the :root variables
    return f":root{{--accent:{accent};--accent-2:{accent_2};--ink:{ink};--muted:{muted};}}"


def _maybe_inline_image(value: str) -> str:
    if value.startswith(("http://", "https://", "data:")):
        return value

    candidate = Path(value)
    if not candidate.is_file():
        return value

    mime, _ = mimetypes.guess_type(candidate.name)
    if mime is None:
        mime = "application/octet-stream"
    encoded = base64.b64encode(candidate.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _inject_scramble_script(html: str) -> str:
    marker = "</body>"
    if marker not in html:
        return html
    return html.replace(marker, f"{_scramble_script()}{marker}")


def _scramble_script() -> str:
    return """
<style>
@media print {
  .scramble-unlock {
    display: none !important;
  }
}
</style>
<script>
(function () {
  const SELECTOR = '[data-scramble="1"]';

  function transformText(text, alphaOffset, digitOffset) {
    const out = [];
    for (let i = 0; i < text.length; i += 1) {
      const ch = text[i];
      const code = ch.charCodeAt(0);
      if (code >= 65 && code <= 90) {
        out.push(String.fromCharCode(((code - 65 + alphaOffset) % 26) + 65));
      } else if (code >= 97 && code <= 122) {
        out.push(String.fromCharCode(((code - 97 + alphaOffset) % 26) + 97));
      } else if (code >= 48 && code <= 57) {
        out.push(String.fromCharCode(((code - 48 + digitOffset) % 10) + 48));
      } else {
        out.push(ch);
      }
    }
    return out.join('');
  }

  function transformHtml(html, alphaOffset, digitOffset) {
    return html.split(/(<[^>]+>)/g).map((part) => {
      if (part.startsWith('<') && part.endsWith('>')) {
        return part;
      }
      return transformText(part, alphaOffset, digitOffset);
    }).join('');
  }

  async function deriveOffsets(key) {
    const data = new TextEncoder().encode(key);
    const hash = await crypto.subtle.digest('SHA-256', data);
    const view = new DataView(hash);
    const offset = view.getUint32(0);
    return {
      alpha: offset % 26,
      digit: offset % 10
    };
  }

  function decodeHref(href, alphaOffset, digitOffset) {
    if (!href) return href;
    if (href.startsWith('mailto:')) {
      const value = href.slice(7);
      return `mailto:${transformText(value, alphaOffset, digitOffset)}`;
    }
    if (href.startsWith('tel:')) {
      const value = href.slice(4);
      return `tel:${transformText(value, alphaOffset, digitOffset)}`;
    }
    return href;
  }

  async function unlockWithKey(key) {
    if (!key) return;
    const offsets = await deriveOffsets(key);
    const alphaOffset = (26 - offsets.alpha) % 26;
    const digitOffset = (10 - offsets.digit) % 10;
    document.querySelectorAll(SELECTOR).forEach((el) => {
      const mode = el.getAttribute('data-scramble-mode');
      if (mode === 'html') {
        el.innerHTML = transformHtml(el.innerHTML, alphaOffset, digitOffset);
      } else {
        el.textContent = transformText(el.textContent || '', alphaOffset, digitOffset);
      }
      if (el.tagName === 'A' && el.getAttribute('data-scramble-href') === '1') {
        el.setAttribute('href', decodeHref(el.getAttribute('href'), alphaOffset, digitOffset));
      }
    });
  }

  function createUnlockUi() {
    const wrapper = document.createElement('div');
    wrapper.className = 'scramble-unlock';
    wrapper.style.position = 'fixed';
    wrapper.style.right = '16px';
    wrapper.style.bottom = '16px';
    wrapper.style.background = 'rgba(15, 23, 42, 0.88)';
    wrapper.style.color = '#fff';
    wrapper.style.padding = '10px';
    wrapper.style.borderRadius = '8px';
    wrapper.style.fontSize = '12px';
    wrapper.style.zIndex = '9999';
    wrapper.style.display = 'flex';
    wrapper.style.gap = '8px';
    wrapper.style.alignItems = 'center';

    const input = document.createElement('input');
    input.type = 'password';
    input.placeholder = 'Unlock key';
    input.style.padding = '6px 8px';
    input.style.borderRadius = '6px';
    input.style.border = '1px solid rgba(148, 163, 184, 0.3)';
    input.style.background = 'rgba(15, 23, 42, 0.35)';
    input.style.color = '#fff';

    const button = document.createElement('button');
    button.textContent = 'Unlock';
    button.style.padding = '6px 10px';
    button.style.borderRadius = '6px';
    button.style.border = 'none';
    button.style.background = '#2563eb';
    button.style.color = '#fff';
    button.style.cursor = 'pointer';

    button.addEventListener('click', () => {
      unlockWithKey(input.value.trim());
    });

    wrapper.appendChild(input);
    wrapper.appendChild(button);
    document.body.appendChild(wrapper);
  }

  const params = new URLSearchParams(window.location.search);
  const keyFromUrl = params.get('unlock');
  if (keyFromUrl) {
    unlockWithKey(keyFromUrl).then(() => {
      params.delete('unlock');
      const newUrl = `${window.location.pathname}${params.toString() ? '?' + params.toString() : ''}`;
      window.history.replaceState({}, '', newUrl);
    });
  }
  createUnlockUi();
})();
</script>
""".strip()
