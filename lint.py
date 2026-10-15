#!/usr/bin/env python3
"""Check the deck's ENS typography, local assets and clean static source."""

from html.parser import HTMLParser
from pathlib import Path
import re
import sys


DEFAULT_HTML = Path(__file__).with_name("index.html")


class DeckParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.slides = []
        self.ids = []
        self.stylesheets = []
        self.external_scripts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section" and "slide" in attrs.get("class", "").split():
            self.slides.append(attrs.get("aria-label"))
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.stylesheets.append(attrs.get("href", ""))
        if tag == "script" and "src" in attrs:
            self.external_scripts.append(attrs["src"])


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_HTML
    html = path.read_text(encoding="utf-8")
    parser = DeckParser()
    parser.feed(html)
    errors = []
    if len(parser.slides) != 8 or not all(parser.slides):
        errors.append("Expected eight labelled slides")
    if len(parser.ids) != len(set(parser.ids)):
        errors.append("Duplicate element IDs")
    if parser.external_scripts or "chrome-extension:" in html:
        errors.append("Unexpected external or browser-save scripts")
    if not re.search(r'<div class="dots" id="dots">\s*</div>', html):
        errors.append("Navigation dots must be generated once at runtime")
    if not re.search(r'\[hidden\]\s*\{\s*display:\s*none\s*!important', html):
        errors.append("Hidden panels must override grid and flex display rules")
    if parser.stylesheets != ["assets/ens.css"]:
        errors.append("Expected the bundled ENS stylesheet")
    css_path = path.parent / "assets/ens.css"
    if not css_path.is_file():
        errors.append("Missing ENS stylesheet")
    else:
        css = css_path.read_text(encoding="utf-8")
        for token, value in {
            "text-small": ".75rem", "text-ui": ".9375rem",
            "text-p": ".9375rem", "text-heading": "1.75rem",
            "heading-weight": "425",
        }.items():
            if not re.search(rf'--{token}:\s*{re.escape(value)}\s*;', css):
                errors.append(f"Unexpected ENS type token: {token}")
        if not re.search(r'\.slide h1\s*\{[^}]*font-size:\s*var\(--text-heading\)', html):
            errors.append("Content headings must use the shared ENS scale")
    for error in errors:
        print(f"FAIL: {error}", file=sys.stderr)
    if not errors:
        print("LSEG deck lint passed: eight slides, ENS typography, local stylesheet and clean navigation.")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
