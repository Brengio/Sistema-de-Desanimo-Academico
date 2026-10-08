import csv
from pathlib import Path

from database.db import delete_simulated_assessments, insert_assessment
from services.assessment_service import construir_avaliacao
from services.risk_calculation import LIMIAR_PADRAO_RISCO

SIMULATED_DATA_NOTICE = 'DADOS SIMULADOS PARA FINS DE VALIDAÇÃO.'


def carregar_dados_simulados(
    database_path: str,
    csv_path: str,
    replace_simulated: bool = False,
) -> dict[str, int]:
    """Importa registros CSV sintéticos e preserva os rótulos esperados para validação."""
    csv_file = Path(csv_path)
    if not csv_file.exists():
        raise FileNotFoundError(f'Arquivo de dados simulados não encontrado: {csv_file}')

    deleted = delete_simulated_assessments(database_path) if replace_simulated else 0
    created = 0
    with csv_file.open('r', encoding='utf-8', newline='') as source:
        reader = csv.DictReader(source)
        for row in reader:
            assessment = construir_avaliacao(
                row,
                limiares=LIMIAR_PADRAO_RISCO,
                risco_esperado=row['expected_risk'],
                eh_simulada=True,
            )
            insert_assessment(database_path, assessment)
            created += 1
    return {'created': created, 'deleted': deleted}
