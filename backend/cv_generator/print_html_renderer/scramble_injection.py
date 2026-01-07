"""Scramble script injection utilities."""


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
</script>""".strip()
