from typing import Optional, Iterable
import re

_MDV2_SPECIALS = ["_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]

def escape_markdown_v2(text: Optional[str]) -> str:
    """Escape all special characters for Telegram MarkdownV2."""
    return escape_markdown_v2_keep(text)

def escape_markdown_v2_keep(text: Optional[str], keep: Iterable[str] = ("*", "_", "`")) -> str:
    """Escape MarkdownV2 specials but keep provided characters unescaped (e.g., for formatting)."""
    if not text:
        return ""
    escaped = text.replace("\\", "\\\\")
    for ch in _MDV2_SPECIALS:
        if ch in keep:
            continue
        escaped = escaped.replace(ch, f"\\{ch}")
    return escaped

def transform_to_markdown_v2(text: Optional[str]) -> str:
    """Best-effort transform from common Markdown to Telegram MarkdownV2.

    - **bold** -> *bold*
    - __italic__ -> _italic_
    - List markers (-, *) at line start -> bullet symbol • (no markdown needed)
    - Escapes other special characters, preserving *, _ and ` for basic formatting
    """
    if not text:
        return ""
    s = text
    # Normalize bold/italic
    s = re.sub(r"\*\*([^*]+)\*\*", r"*\1*", s)
    s = re.sub(r"__([^_]+)__", r"_\1_", s)
    # Replace list markers at start of line with a bullet
    s = re.sub(r"(?m)^[ \t]*[-*]\s+", "• ", s)
    # Escape while keeping basic formatting markers
    s = escape_markdown_v2_keep(s, keep=("*", "_", "`"))
    return s
