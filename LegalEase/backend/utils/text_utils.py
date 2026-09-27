from __future__ import annotations
import html
import re

QUOTE_MAP = {
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",
    "\u2014": "-",
    "\u00a0": " ",
}

def sanitize_text(text: str) -> str:
    if not text:
        return ""
    for source, target in QUOTE_MAP.items():
        text = text.replace(source, target)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def terms_from_text(terms: str) -> list[str]:
    return [x.strip(" -\t") for x in re.split(r";|\n", terms or "") if x.strip(" -\t")]

def text_to_html(text: str) -> str:
    safe = html.escape(sanitize_text(text))
    return "\n".join(
        f"<p>{block.replace(chr(10), '<br>')}</p>"
        for block in safe.split("\n\n")
    )
