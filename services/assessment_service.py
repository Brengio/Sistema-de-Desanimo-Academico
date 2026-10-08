from models.assessment import Assessment
from services.risk_calculation import (
    calcular_pontuacao_contextual,
    calcular_nivel_de_risco,
    calcular_pontuacao_textual,
    calcular_pontuacao_total,
)
from services.sentiment_analysis import analisar_sentimento


def construir_avaliacao(
    dados: dict[str, str],
    limiares: dict[str, int],
    risco_esperado: str | None = None,
    eh_simulada: bool = False,
) -> Assessment:
    """Executa o pipeline computacional completo para uma entrada validada."""
    sentimento = analisar_sentimento(dados['text_response'])
    contextual = calcular_pontuacao_contextual(
        dados['academic_workload'],
        dados['difficulty'],
        dados['satisfaction'],
        dados['motivation'],
    )
    pontuacao_textual = calcular_pontuacao_textual(str(sentimento['polarity']))
    pontuacao_total = calcular_pontuacao_total(int(contextual['total_score']), pontuacao_textual)
    classificacao = calcular_nivel_de_risco(pontuacao_total, limiares)

    return Assessment(
        course=dados['course'],
        semester=int(dados['semester']),
        academic_workload=dados['academic_workload'],
        difficulty=dados['difficulty'],
        satisfaction=dados['satisfaction'],
        motivation=dados['motivation'],
        text_response=dados['text_response'],
        text_polarity=str(sentimento['polarity']),
        text_score=pontuacao_textual,
        positive_terms=list(sentimento['positive_terms']),
        negative_terms=list(sentimento['negative_terms']),
        contextual_score=int(contextual['total_score']),
        total_score=pontuacao_total,
        risk_level=str(classificacao['risk_level']),
        expected_risk=risco_esperado,
        is_simulated=eh_simulada,
    )
