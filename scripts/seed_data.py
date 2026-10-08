"""Load the synthetic validation dataset into the local SQLite database."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import create_app
from services.simulated_data import carregar_dados_simulados


def main() -> None:
    parser = argparse.ArgumentParser(description='Carrega os dados simulados no SQLite.')
    parser.add_argument('--replace', action='store_true', help='Substitui os registros sintéticos já existentes.')
    arguments = parser.parse_args()

    app = create_app({'AUTO_CARREGAR_DADOS_SIMULADOS': False})
    result = carregar_dados_simulados(
        app.config['DATABASE_PATH'],
        app.config['SIMULATED_DATA_PATH'],
        replace_simulated=arguments.replace,
    )
    print(f"{result['created']} registros carregados; {result['deleted']} registros sintéticos removidos.")


if __name__ == '__main__':
    main()
