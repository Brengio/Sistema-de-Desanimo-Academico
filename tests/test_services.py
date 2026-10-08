from services.risk_calculation import (
    calcular_pontuacao_contextual,
    calcular_nivel_de_risco,
    calcular_pontuacao_textual,
    calcular_pontuacao_total,
)
from services.sentiment_analysis import analisar_sentimento
from services.text_processing import preprocess_text


def test_preprocess_text_normalizes_and_removes_stopwords():
    processed = preprocess_text('Estou MUITO cansado!!! Não consigo acompanhar as matérias.')
    assert processed['normalized_text'] == 'estou muito cansado não consigo acompanhar as matérias'
    assert 'cansado' in processed['relevant_tokens']
    assert 'não' in processed['relevant_tokens']
    assert 'muito' not in processed['relevant_tokens']


def test_sentiment_analysis_identifies_negative_terms():
    result = analisar_sentimento('Estou cansado, desmotivado e com muita dificuldade.')
    assert result['polarity'] == 'negative'
    assert result['score'] < 0
    assert 'cansado' in result['negative_terms']
    assert 'desmotivado' in result['negative_terms']


def test_risk_rules_follow_expected_boundaries():
    contextual = calcular_pontuacao_contextual('Alta', 'Alta', 'Insatisfeito', 'Baixa')
    assert contextual['total_score'] == 8
    assert calcular_pontuacao_textual('positive') == 0
    assert calcular_pontuacao_total(6, 1) == 7
    assert calcular_nivel_de_risco(3)['risk_level'] == 'Baixo'
    assert calcular_nivel_de_risco(4)['risk_level'] == 'Médio'
    assert calcular_nivel_de_risco(7)['risk_level'] == 'Alto'
