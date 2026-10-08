from services.text_processing import preprocess_text

# An explicit lexical baseline makes the first TCC version inspectable and replaceable.
POSITIVE_LEXICON = frozenset(
    {
        'animado', 'animada', 'aprendendo', 'apoio', 'confiante', 'clareza', 'conseguido',
        'conseguir', 'entusiasmado', 'entusiasmada', 'feliz', 'gostando', 'interessante',
        'motivado', 'motivada', 'organização', 'organizado', 'organizada', 'progresso',
        'realizado', 'realizada', 'satisfeito', 'satisfeita', 'tranquilidade', 'tranquilo',
        'tranquila', 'valorizado', 'valorizada', 'melhorar', 'positivo', 'positiva',
    }
)

NEGATIVE_LEXICON = frozenset(
    {
        'abandonar', 'abandono', 'ansiedade', 'ansioso', 'ansiosa', 'atrasado', 'atrasada',
        'cansado', 'cansada', 'confuso', 'confusa', 'desanimado', 'desanimada', 'desistir',
        'desmotivada', 'desmotivado', 'dificuldade', 'dificuldades', 'difícil', 'difíceis',
        'esgotado', 'esgotada', 'estressado', 'estressada', 'exausto', 'exausta', 'frustrado',
        'frustrada', 'insegurança', 'inseguro', 'insegura', 'perdido', 'perdida', 'pressão',
        'preocupado', 'preocupada', 'sobrecarregado', 'sobrecarregada', 'saturado', 'saturada',
        'triste', 'tristeza', 'desistência', 'isolado', 'isolada',
    }
)

PHRASE_SIGNALS = {
    'não consigo': 'negative',
    'não aguento': 'negative',
    'quero continuar': 'positive',
    'estou gostando': 'positive',
}


class SentilexAdapter:
    """Extension point reserved for a future SentiLex-PT implementation."""

    name = 'lexico_simples_ptbr'
    available = False

    def analyze(self, _: str) -> None:
        raise NotImplementedError(
            'A integração com SentiLex-PT pode substituir este adaptador sem alterar as rotas.'
        )


def _unique_in_order(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def analisar_sentimento(texto: str) -> dict[str, object]:
    """Analisa a polaridade léxica e retorna termos e pontuação normalizada."""
    processed = preprocess_text(texto)
    tokens = processed['tokens']
    normalized_text = processed['normalized_text']

    positive_terms = [token for token in tokens if token in POSITIVE_LEXICON]
    negative_terms = [token for token in tokens if token in NEGATIVE_LEXICON]

    for phrase, polarity in PHRASE_SIGNALS.items():
        if phrase in normalized_text:
            if polarity == 'positive':
                positive_terms.append(phrase)
            else:
                negative_terms.append(phrase)

    positive_terms = _unique_in_order(positive_terms)
    negative_terms = _unique_in_order(negative_terms)
    positive_count = len(positive_terms)
    negative_count = len(negative_terms)
    total_terms = positive_count + negative_count

    if total_terms == 0:
        score = 0.0
        polarity = 'neutral'
    else:
        score = round((positive_count - negative_count) / total_terms, 2)
        if score > 0:
            polarity = 'positive'
        elif score < 0:
            polarity = 'negative'
        else:
            polarity = 'neutral'

    return {
        'polarity': polarity,
        'score': score,
        'positive_terms': positive_terms,
        'negative_terms': negative_terms,
        'processed_text': processed,
        'engine': SentilexAdapter.name,
    }
