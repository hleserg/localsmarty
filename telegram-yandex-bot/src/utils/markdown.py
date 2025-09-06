from typing import Optional

_MDV2_SPECIALS = r"_ * [ ] ( ) ~ ` > # + - = | { } . !".split()

def escape_markdown_v2(text: Optional[str]) -> str:
    """Escape special characters for Telegram MarkdownV2.

    This escapes: _ * [ ] ( ) ~ ` > # + - = | { } . ! and backslashes.
    See: https://core.telegram.org/bots/api#markdownv2-style
    """
    if not text:
        return ""
    # First escape backslash
    escaped = text.replace("\\", "\\\\")
    for ch in ["_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]:
        escaped = escaped.replace(ch, f"\\{ch}")
    return escaped
