"""Generate 300 varied synthetic records for deterministic rule validation."""
import csv
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import Config
from services.assessment_service import construir_avaliacao

OUTPUT_PATH = ROOT / 'data' / 'simulated_data.csv'
RANDOM = random.Random(20260829)
COURSES = ['Ciência da Computação', 'Administração', 'Sistemas de Informação', 'Engenharia']

TEXT_PARTS = {
    'Baixo': {
        'openers': [
            'Estou motivado com o curso', 'Sinto-me confiante neste semestre',
            'Tenho gostado bastante das disciplinas', 'Estou satisfeito com meu progresso',
            'Sigo animado para continuar aprendendo', 'Percebo clareza nos objetivos do curso',
            'Estou entusiasmado com os conteúdos', 'Tenho me sentido tranquilo para estudar',
            'O semestre tem sido positivo para mim', 'Sinto que estou conseguindo evoluir',
        ],
        'middles': [
            'e consigo acompanhar as atividades', 'com boa organização da rotina',
            'e encontro apoio quando preciso', 'mesmo com desafios pontuais',
            'e mantenho um ritmo de estudos', 'com interesse nas aulas',
            'e percebo progresso nas disciplinas', 'com tranquilidade na maior parte da semana',
            'e consigo planejar minhas entregas', 'com participação nas atividades propostas',
        ],
        'endings': [
            'Tenho vontade de seguir no curso.', 'Quero continuar construindo meu aprendizado.',
            'A experiência acadêmica tem sido importante para mim.', 'Vejo sentido em continuar estudando.',
            'Estou satisfeito com os avanços alcançados.', 'Pretendo manter essa dedicação.',
            'A rotina está equilibrada neste momento.', 'Isso reforça minha motivação.',
            'Consigo perceber resultados do meu esforço.', 'Estou preparado para os próximos desafios.',
        ],
    },
    'Médio': {
        'openers': [
            'Tenho enfrentado dificuldade em algumas disciplinas', 'A carga de atividades tem exigido atenção',
            'Estou me sentindo cansado em alguns períodos', 'Algumas matérias estão mais difíceis do que esperava',
            'Minha organização ainda precisa melhorar', 'A rotina de estudos ficou mais intensa',
            'Em certos dias sinto alguma pressão acadêmica', 'Tenho dúvidas sobre parte dos conteúdos',
            'O ritmo das entregas tem sido desafiador', 'Ainda estou tentando equilibrar as demandas',
            'Tenho oscilado na motivação durante o semestre', 'Nem sempre consigo acompanhar tudo como gostaria',
        ],
        'middles': [
            'mas ainda quero continuar no curso', 'e estou buscando novas formas de estudar',
            'porém encontro apoio de colegas', 'mas acredito que posso melhorar gradualmente',
            'e tento organizar uma rotina mais estável', 'porém sigo interessado na formação',
            'e procuro conversar quando necessário', 'mas não pretendo desistir das disciplinas',
            'e espero recuperar o ritmo nas próximas semanas', 'porém mantenho metas para o semestre',
        ],
        'endings': [
            'Preciso ajustar minhas estratégias de estudo.', 'Acredito que um planejamento melhor pode ajudar.',
            'Quero encontrar um equilíbrio na rotina.', 'Ainda vejo valor em concluir esta formação.',
            'Estou tentando lidar com essas dificuldades.', 'Um acompanhamento acadêmico poderia ser útil.',
            'Espero me sentir mais seguro nas próximas atividades.', 'Continuo procurando apoio para avançar.',
            'Quero melhorar minha organização aos poucos.', 'A situação exige atenção, mas sigo empenhado.',
        ],
    },
    'Alto': {
        'openers': [
            'Estou muito desmotivado com o curso', 'Sinto-me cansado e sobrecarregado',
            'Não consigo acompanhar as atividades', 'Tenho dificuldade constante nas disciplinas',
            'Estou esgotado com a rotina acadêmica', 'A pressão das entregas tem sido muito grande',
            'Tenho me sentido frustrado com meu desempenho', 'Estou preocupado e inseguro sobre continuar',
            'As matérias parecem difíceis demais neste momento', 'Sinto que perdi o interesse pelas aulas',
        ],
        'middles': [
            'e penso em abandonar algumas disciplinas', 'porque não consigo organizar todas as demandas',
            'e minha motivação está muito baixa', 'pois a dificuldade aumentou bastante',
            'e estou com receio de não conseguir continuar', 'porque me sinto perdido com os conteúdos',
            'e a sobrecarga tem afetado minha rotina', 'pois estou frustrado com a quantidade de tarefas',
            'e não vejo como recuperar o ritmo sozinho', 'porque a pressão está se tornando constante',
        ],
        'endings': [
            'Preciso de apoio para lidar com a situação acadêmica.', 'A continuidade no curso parece difícil agora.',
            'Gostaria de encontrar uma alternativa para essas dificuldades.', 'Sinto que preciso reorganizar totalmente a rotina.',
            'O semestre tem sido muito desgastante.', 'Não sei como avançar nas atividades atuais.',
            'A situação está comprometendo meu engajamento.', 'Tenho dificuldade para visualizar uma melhora próxima.',
            'O acompanhamento acadêmico seria importante neste momento.', 'A carga atual parece insustentável para mim.',
        ],
    },
}

CONTEXT_PROFILES = {
    'Baixo': [
        ('Baixa', 'Baixa', 'Satisfeito', 'Alta'),
        ('Moderada', 'Baixa', 'Satisfeito', 'Moderada'),
        ('Alta', 'Baixa', 'Satisfeito', 'Alta'),
        ('Moderada', 'Baixa', 'Neutro', 'Alta'),
        ('Baixa', 'Moderada', 'Muito satisfeito', 'Alta'),
    ],
    'Médio': [
        ('Moderada', 'Moderada', 'Neutro', 'Moderada'),
        ('Alta', 'Baixa', 'Neutro', 'Moderada'),
        ('Moderada', 'Alta', 'Satisfeito', 'Moderada'),
        ('Baixa', 'Alta', 'Neutro', 'Moderada'),
        ('Moderada', 'Moderada', 'Insatisfeito', 'Alta'),
    ],
    'Alto': [
        ('Alta', 'Alta', 'Neutro', 'Moderada'),
        ('Muito alta', 'Alta', 'Insatisfeito', 'Baixa'),
        ('Alta', 'Moderada', 'Muito insatisfeito', 'Baixa'),
        ('Moderada', 'Alta', 'Insatisfeito', 'Baixa'),
        ('Alta', 'Muito alta', 'Insatisfeito', 'Muito baixa'),
    ],
}


def build_text(level: str, course: str, semester: int) -> str:
    parts = TEXT_PARTS[level]
    return (
        f'{RANDOM.choice(parts["openers"])}, {RANDOM.choice(parts["middles"])}. '
        f'{RANDOM.choice(parts["endings"])} Estou no {semester}º semestre de {course}.'
    )


def generate() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    record_id = 1
    for expected_risk in ('Baixo', 'Médio', 'Alto'):
        for _ in range(100):
            course = RANDOM.choice(COURSES)
            semester = RANDOM.randint(1, 10)
            workload, difficulty, satisfaction, motivation = RANDOM.choice(CONTEXT_PROFILES[expected_risk])
            text_response = build_text(expected_risk, course, semester)
            payload = {
                'course': course,
                'semester': str(semester),
                'academic_workload': workload,
                'difficulty': difficulty,
                'satisfaction': satisfaction,
                'motivation': motivation,
                'text_response': text_response,
            }
            actual = construir_avaliacao(payload, Config.LIMIAR_DE_RISCO).risk_level
            if actual != expected_risk:
                raise RuntimeError(
                    f'Perfil sintético inconsistente: esperado {expected_risk}, calculado {actual}.'
                )
            rows.append({**payload, 'id': record_id, 'expected_risk': expected_risk})
            record_id += 1

    fieldnames = [
        'id', 'course', 'semester', 'academic_workload', 'difficulty', 'satisfaction',
        'motivation', 'text_response', 'expected_risk',
    ]
    with OUTPUT_PATH.open('w', encoding='utf-8', newline='') as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f'Arquivo gerado com {len(rows)} registros: {OUTPUT_PATH}')


if __name__ == '__main__':
    generate()
