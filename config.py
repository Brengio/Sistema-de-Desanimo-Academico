import os
from pathlib import Path


class Config:
    """Configuração centralizada para a aplicação Flask local."""

    BASE_DIR = Path(__file__).resolve().parent
    SECRET_KEY = os.environ.get('SECRET_KEY', 'chave-local-desenvolvimento-tcc')
    DATABASE_PATH = str(BASE_DIR / 'database' / 'academic_motivation.db')
    SIMULATED_DATA_PATH = str(BASE_DIR / 'data' / 'simulated_data.csv')
    MAX_TEXT_LENGTH = 1000
    AUTO_CARREGAR_DADOS_SIMULADOS = True

    COURSES = (
        'Ciência da Computação',
        'Administração',
        'Sistemas de Informação',
        'Engenharia',
        'Outro',
    )
    SEMESTERS = tuple(range(1, 11))

    # Centraliza os limites configuráveis da classificação.
    LIMIAR_DE_RISCO = {
        'low_max': 3,
        'medium_max': 6,
        'max_score': 10,
    }
