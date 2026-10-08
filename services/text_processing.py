import re
import unicodedata

# The negator "não" is intentionally not a stopword because it may change sentiment.
PORTUGUESE_STOPWORDS = frozenset(
    {
        'a', 'ao', 'aos', 'as', 'à', 'às', 'com', 'como', 'da', 'das', 'de', 'do', 'dos',
        'e', 'é', 'em', 'na', 'nas', 'no', 'nos', 'o', 'os', 'ou', 'para', 'por', 'que',
        'se', 'sem', 'um', 'uma', 'uns', 'umas', 'sobre', 'entre', 'até', 'após', 'já',
        'mais', 'muito', 'muita', 'muitos', 'muitas', 'me', 'minha', 'meu', 'meus', 'minhas',
        'você', 'vocês', 'ele', 'ela', 'eles', 'elas', 'isso', 'isto', 'aquele', 'aquela',
        'tenho', 'tem', 'ter', 'ser', 'estar', 'estou', 'está', 'estão', 'foi', 'são',
        'também', 'ainda', 'mas', 'porque', 'quando', 'onde', 'qual', 'quais', 'cada',
        'algum', 'alguma', 'alguns', 'algumas', 'apenas', 'bem', 'mesmo', 'mesma', 'mesmos',
    }
)


def normalize_text(text: str) -> str:
    """Normalize whitespace, Unicode representation and letter casing."""
    normalized = unicodedata.normalize('NFKC', text or '').lower()
    normalized = re.sub(r'[^a-zà-ÿ0-9\s-]', ' ', normalized, flags=re.IGNORECASE)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized


def tokenize(normalized_text: str) -> list[str]:
    """Tokenize Brazilian Portuguese text with a transparent regular expression."""
    return re.findall(r'[a-zà-ÿ]+', normalized_text, flags=re.IGNORECASE)


def remove_stopwords(tokens: list[str]) -> list[str]:
    """Remove frequent Portuguese function words while preserving negation."""
    return [token for token in tokens if token not in PORTUGUESE_STOPWORDS]


def preprocess_text(text: str) -> dict[str, object]:
    """Return auditable intermediate information for future NLP replacements."""
    normalized = normalize_text(text)
    tokens = tokenize(normalized)
    relevant_tokens = remove_stopwords(tokens)
    return {
        'original_text': text,
        'normalized_text': normalized,
        'tokens': tokens,
        'relevant_tokens': relevant_tokens,
    }
