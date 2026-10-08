from typing import Mapping

LIMIAR_PADRAO_RISCO = {'low_max': 3, 'medium_max': 6, 'max_score': 10}

CONTEXTUAL_RULES = {
    'academic_workload': {
        'Muito baixa': 0,
        'Baixa': 0,
        'Moderada': 1,
        'Alta': 2,
        'Muito alta': 2,
    },
    'difficulty': {
        'Muito baixa': 0,
        'Baixa': 0,
        'Moderada': 1,
        'Alta': 2,
        'Muito alta': 2,
    },
    'satisfaction': {
        'Muito satisfeito': 0,
        'Satisfeito': 0,
        'Neutro': 1,
        'Insatisfeito': 2,
        'Muito insatisfeito': 2,
    },
    'motivation': {
        'Muito alta': 0,
        'Alta': 0,
        'Moderada': 1,
        'Baixa': 2,
        'Muito baixa': 2,
    },
}

TEXTUAL_RULES = {'positive': 0, 'neutral': 1, 'negative': 2}

FACTOR_DESCRIPTIONS = {
    'academic_workload': {1: 'Carga acadêmica moderada.', 2: 'Carga acadêmica elevada.'},
    'difficulty': {1: 'Dificuldade moderada para acompanhar disciplinas.', 2: 'Dificuldade elevada para acompanhar disciplinas.'},
    'satisfaction': {1: 'Satisfação neutra com o curso.', 2: 'Baixa satisfação com o curso.'},
    'motivation': {1: 'Motivação moderada para continuar o curso.', 2: 'Baixa motivação para continuar o curso.'},
}


def calcular_pontuacao_contextual(
    academic_workload: str,
    difficulty: str,
    satisfaction: str,
    motivation: str,
) -> dict[str, object]:
    """Transforma as quatro respostas acadêmicas em uma pontuação transparente de 0 a 8."""
    answers = {
        'academic_workload': academic_workload,
        'difficulty': difficulty,
        'satisfaction': satisfaction,
        'motivation': motivation,
    }
    components: dict[str, int] = {}
    for field, answer in answers.items():
        try:
            components[field] = CONTEXTUAL_RULES[field][answer]
        except KeyError as exc:
            raise ValueError(f'Resposta contextual inválida para {field}: {answer}') from exc
    return {'total_score': sum(components.values()), 'components': components}


def calcular_pontuacao_textual(polarity: str) -> int:
    """Converte a polaridade léxica na contribuição textual de risco entre 0 e 2."""
    try:
        return TEXTUAL_RULES[polarity]
    except KeyError as exc:
        raise ValueError(f'Polaridade textual inválida: {polarity}') from exc


def calcular_pontuacao_total(contextual_score: int, text_score: int) -> int:
    """Combina as pontuações contextual e textual com limites explícitos."""
    return min(LIMIAR_PADRAO_RISCO['max_score'], max(0, contextual_score + text_score))


def calcular_nivel_de_risco(
    score: int,
    thresholds: Mapping[str, int] | None = None,
) -> dict[str, object]:
    """Classifica um total usando limiares configuráveis e centralizados."""
    limits = dict(LIMIAR_PADRAO_RISCO)
    if thresholds:
        limits.update(thresholds)

    if not 0 <= score <= limits['max_score']:
        raise ValueError(f'A pontuação total deve estar entre 0 e {limits["max_score"]}.')
    if score <= limits['low_max']:
        risk_level = 'Baixo'
    elif score <= limits['medium_max']:
        risk_level = 'Médio'
    else:
        risk_level = 'Alto'
    return {'total_score': score, 'risk_level': risk_level}


def identificar_fatores(
    contextual_components: Mapping[str, int],
    text_polarity: str,
) -> list[str]:
    """Produz uma lista explicável de fatores para a tela de resultado."""
    factors: list[str] = []
    for field, points in contextual_components.items():
        if points > 0:
            factors.append(FACTOR_DESCRIPTIONS[field][points])
    if text_polarity == 'negative':
        factors.append('Polaridade textual negativa identificada.')
    elif text_polarity == 'neutral':
        factors.append('Polaridade textual neutra identificada.')
    else:
        factors.append('Polaridade textual positiva identificada.')
    return factors
