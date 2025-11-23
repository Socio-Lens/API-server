import re
import html
import string
from typing import Iterable, List

_URL_RE = re.compile(r"https?://\S+|www\.\S+", flags=re.IGNORECASE)
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_MENTION_RE = re.compile(r"@\w+")
_HASHTAG_RE = re.compile(r"#")

# Basic emoji pattern covering common blocks
_EMOJI_RE = re.compile(
    (
        "[\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251]"
    ),
    flags=re.UNICODE,
)

_MULTI_WS_RE = re.compile(r"\s+")
_MULTI_NEWLINE_RE = re.compile(r"\n\s*\n+")


def clean_text(
    text: str,
    lower: bool = False,
    strip_html: bool = False,
    remove_urls: bool = False,
    remove_mentions: bool = False,
    remove_hashtag_symbol: bool = False,
    remove_emojis: bool = False,
    remove_punctuation: bool = False,
    normalize_newlines: bool = False,
    normalize_whitespace: bool = False,
    preserve_case_words: Iterable[str] = (),
) -> str:
    """Perform lightweight, configurable text cleaning.

    Args:
        text: Input string to clean.
        lower: Convert text to lowercase (applied after other removals).
        strip_html: Remove HTML tags and unescape HTML entities.
        remove_urls: Remove http/https and www URLs.
        remove_mentions: Remove Twitter-style @mentions.
        remove_hashtag_symbol: Remove the leading '#' from hashtags but keep the word.
        remove_emojis: Remove emoji characters.
        remove_punctuation: Strip ASCII punctuation characters.
            normalize_newlines: Collapse repeated blank lines to a single newline.
            normalize_whitespace: Collapse repeated whitespace to single spaces and trim.

    Returns:
        Cleaned string.

    Notes:
        - This function intentionally avoids heavy NLP dependencies. For
          lemmatization or stopword removal, integrate with spaCy or NLTK
          outside this utility.
    """
    if not text:
        return ""

    text = str(text)

    if strip_html:
        text = _HTML_TAG_RE.sub(" ", text)
        text = html.unescape(text)

    if remove_urls:
        text = _URL_RE.sub(" ", text)

    if remove_mentions:
        text = _MENTION_RE.sub(" ", text)

    if remove_hashtag_symbol:
        text = _HASHTAG_RE.sub("", text)

    if remove_emojis:
        text = _EMOJI_RE.sub("", text)

    if remove_punctuation:
        trans = str.maketrans("", "", string.punctuation)
        text = text.translate(trans)

    if normalize_newlines:
        # Collapse multiple consecutive newlines (and intervening whitespace)
        # into a single newline. Note: if `normalize_whitespace=True` is set
        # afterwards it will replace newlines with spaces, so set
        # `normalize_whitespace=False` when you want to preserve newlines.
        text = _MULTI_NEWLINE_RE.sub("\n", text)

    if normalize_whitespace:
        text = _MULTI_WS_RE.sub(" ", text).strip()

    if lower:
        if preserve_case_words:
            placeholders = {}
            for i, w in enumerate(preserve_case_words):
                key = f"__PRESERVE_{i}__"
                placeholders[key] = w
                text = re.sub(rf"\b{re.escape(w)}\b", key, text)

            text = text.lower()

            for key, w in placeholders.items():
                text = text.replace(key, w)
        else:
            text = text.lower()

    return text


def clean_texts(texts: Iterable[str], **kwargs) -> List[str]:
    """Apply `clean_text` to an iterable of strings and return a list."""
    return [clean_text(t, **kwargs) for t in texts]


if __name__ == "__main__":
    examples = [
        "<p>Hello World! Visit https://example.com 👋 #Welcome @user</p>",
        "Here's some mixed TEXT — with punctuation!!! and emojis 😊😊",
    ]
    for e in examples:
        print("Original:", e)
        print("Cleaned:", clean_text(e))
        print()
