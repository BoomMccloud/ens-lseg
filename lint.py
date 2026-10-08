#!/usr/bin/env python3
"""Check that the LSEG deck uses slide 2's panel text scale.

Run with ``python3 lint.py``. An optional HTML path makes it possible
to check a draft without replacing the deck.
"""

from pathlib import Path
import re
import sys


DEFAULT_HTML = Path(__file__).with_name("index.html")

# Slide 2 establishes the scale: names 17, section titles 16, values 14,
# labels and addresses 12, metadata 11, and controls 13 or larger.
EXPECTED = {
    ".registry-panel .treeitem b": "17px",
    ".registry-panel .treeitem span": "12px",
    ".registry-panel .csvtitle": "16px",
    ".registry-panel .asset-item b": "14px",
    ".registry-panel .asset-item small": "12px",
    ".registry-panel .micro": "11px",
    ".registry-panel .pill": "11px",
    ".registry-panel .action": "13px",
    ".summary b": "17px",
    ".result-identity b": "17px",
    ".picker-top b": "16px",
    ".fact b": "14px",
    ".asset-item b": "14px",
    ".picker-row strong": "14px",
    ".address-row strong": "14px",
    ".eyelabel": "12px",
    ".fact span": "12px",
    ".candidate span": "12px",
    ".asset-item small": "12px",
    ".picker-row small": "12px",
    ".result-identity small": "12px",
    ".summary small": "12px",
    ".candidate code": "12px",
    ".resolved code": "12px",
    ".address-row code": "12px",
    ".action": "13px",
    ".compare-tab": "14px",
    ".micro": "11px",
    ".pill": "11px",
    ".note": "11px",
    ".resolved-badge": "11px",
    ".verification": "11px",
    ".source-tag": "11px",
}
INPUTS = (".lookupbar input", ".ticker-search input", ".searchinput")


def css_rules(css: str, max_width: int | None = None):
    """Yield (media max width, selectors, font size) from simple CSS blocks."""
    pos = 0
    while (opening := css.find("{", pos)) != -1:
        prelude = css[pos:opening].strip()
        depth = 1
        closing = opening + 1
        while closing < len(css) and depth:
            if css[closing] == "{":
                depth += 1
            elif css[closing] == "}":
                depth -= 1
            closing += 1
        if depth:
            raise ValueError("Unclosed CSS block")
        body = css[opening + 1 : closing - 1]
        if prelude.startswith("@media"):
            match = re.search(r"max-width\s*:\s*(\d+)px", prelude)
            if match:
                width = int(match.group(1))
                yield from css_rules(body, min(width, max_width) if max_width else width)
        elif not prelude.startswith("@"):
            sizes = re.findall(r"(?:^|;)\s*font-size\s*:\s*([^;]+)", body)
            if sizes:
                selectors = tuple(selector.strip() for selector in prelude.split(","))
                yield max_width, selectors, sizes[-1].strip()
        pos = closing


def main() -> int:
    html_file = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_HTML
    if not html_file.exists():
        print(f"FAIL: Missing slide deck: {html_file}", file=sys.stderr)
        return 1
    html = html_file.read_text(encoding="utf-8")
    match = re.search(r"<style\b[^>]*>(.*?)</style\s*>", html, re.I | re.S)
    if not match:
        print("FAIL: No embedded stylesheet found.", file=sys.stderr)
        return 1
    css = re.sub(r"/\*.*?\*/", "", match.group(1), flags=re.S)
    try:
        rules = list(css_rules(css))
    except ValueError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    errors = []
    for width in (1024, 390):
        expected = EXPECTED | {selector: "16px" if width == 390 else "15px" for selector in INPUTS}
        actual = {}
        for media_width, selectors, size in rules:
            if media_width is None or width <= media_width:
                for selector in selectors:
                    if selector in expected:
                        actual[selector] = size
        for selector, size in expected.items():
            if actual.get(selector) != size:
                errors.append(
                    f"{width}px: {selector} must be {size}; found {actual.get(selector, 'no font-size rule')}"
                )

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"LSEG typography lint passed at desktop and mobile widths ({len(EXPECTED) + len(INPUTS)} selectors).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
