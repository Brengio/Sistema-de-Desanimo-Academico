from database.db import count_assessments, get_assessment_by_id


def valid_form_data():
    return {
        'course': 'Ciência da Computação',
        'semester': '3',
        'academic_workload': 'Alta',
        'difficulty': 'Alta',
        'satisfaction': 'Insatisfeito',
        'motivation': 'Baixa',
        'text_response': 'Estou cansado, desmotivado e com muita dificuldade para acompanhar as atividades.',
    }


def test_dashboard_is_available(client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'Painel de acompanhamento'.encode() in response.data


def test_assessment_submission_saves_and_redirects(client, app):
    response = client.post('/nova-avaliacao', data=valid_form_data(), follow_redirects=False)
    assert response.status_code == 302
    assert '/resultado/1' in response.headers['Location']
    assert count_assessments(app.config['DATABASE_PATH']) == 1
    assessment = get_assessment_by_id(app.config['DATABASE_PATH'], 1)
    assert assessment is not None
    assert assessment.risk_level == 'Alto'
    assert assessment.total_score >= 7


def test_assessment_validation_returns_errors(client):
    response = client.post('/nova-avaliacao', data={'course': 'Ciência da Computação'}, follow_redirects=True)
    assert response.status_code == 200
    assert 'Não foi possível concluir a análise'.encode() in response.data


def test_dashboard_api_returns_aggregates(client):
    client.post('/nova-avaliacao', data=valid_form_data())
    response = client.get('/api/dashboard')
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['total'] == 1
    assert payload['risk_counts']['Alto'] == 1
