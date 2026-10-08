from pathlib import Path

from flask import Flask

from config import Config
from database.db import count_assessments, init_db
from routes.api_routes import api_bp
from routes.assessment_routes import assessment_bp
from routes.dashboard_routes import dashboard_bp
from routes.main_routes import main_bp
from services.simulated_data import carregar_dados_simulados


def create_app(test_config: dict | None = None) -> Flask:
    """Create and configure the academic-indicator application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    Path(app.config['DATABASE_PATH']).parent.mkdir(parents=True, exist_ok=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    init_db(app.config['DATABASE_PATH'])

    app.register_blueprint(main_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)

    if app.config.get('AUTO_CARREGAR_DADOS_SIMULADOS', True):
        database_path = app.config['DATABASE_PATH']
        csv_path = app.config['SIMULATED_DATA_PATH']
        if count_assessments(database_path) == 0 and Path(csv_path).exists():
            carregar_dados_simulados(database_path, csv_path, replace_simulated=False)

    @app.template_filter('polarity_label')
    def polarity_label(value: str) -> str:
        return {
            'positive': 'Positiva',
            'neutral': 'Neutra',
            'negative': 'Negativa',
        }.get(value, 'Não identificada')

    @app.template_filter('risk_class')
    def risk_class(value: str) -> str:
        return {
            'Baixo': 'risk-low',
            'Médio': 'risk-medium',
            'Alto': 'risk-high',
        }.get(value, 'risk-neutral')

    @app.context_processor
    def inject_template_context() -> dict:
        return {
            'system_notice': (
                'Classificação computacional de indicadores acadêmicos. '
                'Não constitui diagnóstico psicológico, clínico ou médico.'
            )
        }

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=True)
