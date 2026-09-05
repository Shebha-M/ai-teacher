"""Text cleaning pipeline for extracted educational documents."""
import re
import unicodedata


class TextCleaner:
    """Cleans and normalizes extracted text while preserving educational structure."""

    @classmethod
    def clean(cls, text: str) -> str:
        if not text:
            return ""

        # 1. Normalize unicode (e.g., smart quotes, ligatures like fi -> fi)
        cleaned = unicodedata.normalize("NFKC", text)

        # 2. Normalize line endings (\r\n -> \n, \r -> \n)
        cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")

        # 3. Strip non-printable / zero-width characters (except valid tabs & newlines)
        cleaned = "".join(ch for ch in cleaned if ch in ("\n", "\t") or (ord(ch) >= 32 and ord(ch) != 127))

        # 4. Fix hyphenated line breaks (e.g., "algo-\nrithm" -> "algorithm")
        cleaned = re.sub(r"(\w+)-\n(\w+)", r"\1\2", cleaned)

        # 5. Collapse multiple horizontal spaces/tabs to a single space
        lines = []
        for line in cleaned.split("\n"):
            # Collapse spaces/tabs within each line
            line_cleaned = re.sub(r"[ \t]+", " ", line).strip()
            lines.append(line_cleaned)

        cleaned = "\n".join(lines)

        # 6. Normalize paragraph spacing (max 2 consecutive newlines)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

        return cleaned.strip()
