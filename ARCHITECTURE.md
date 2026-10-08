# Arquitetura do Sistema de Detecção de Desânimo Acadêmico

**Versão:** 1.0 — base para TCC  
**Autor:** Breno Giovani Roman Pais Seles  
**Data:** 29 de agosto de 2026

## 1. Decisão arquitetural

O projeto adota uma arquitetura monolítica modular em **Python/Flask**, com persistência local em **SQLite**, páginas renderizadas no servidor por **Jinja** e interações leves em JavaScript. A escolha favorece instalação local, baixo acoplamento entre responsabilidades e explicação objetiva em um Trabalho de Conclusão de Curso. Flask oferece suporte direto a rotas, templates, arquivos estáticos e padrões para aplicações estruturadas, enquanto SQLite permite distribuir o banco como um único arquivo local. [1] [2]

A interface usa Bootstrap 5 para responsividade e componentes visuais, e Chart.js para apresentar os indicadores em gráficos de canvas atualizados a cada carregamento do dashboard. [3]

> **Escopo ético:** esta aplicação não realiza diagnóstico psicológico, médico ou de saúde mental. Ela produz somente uma classificação computacional de indicadores associados ao contexto acadêmico para apoiar o acompanhamento pedagógico.

| Camada | Responsabilidade | Componentes principais |
|---|---|---|
| Apresentação | Exibir dashboards, formulários, tabelas, validação e relatórios | `templates/`, `static/css/`, `static/js/` |
| Rotas | Receber requisições, validar entradas, compor respostas HTTP | `routes/` |
| Domínio e serviços | Processar texto, analisar léxico e calcular risco | `services/` |
| Persistência | Representar e consultar avaliações | `models/assessment.py`, `database/db.py` |
| Dados de validação | Gerar, importar e validar registros sintéticos | `data/`, `scripts/` |

## 2. Estrutura de pastas

```text
sistema-desanimo-academico-flask/
├── app.py                         # Fábrica da aplicação e registro de blueprints
├── config.py                      # Configurações centralizadas e limites de risco
├── requirements.txt               # Dependências Python
├── README.md                      # Guia de instalação, uso e limitações
├── ARCHITECTURE.md                # Este documento de arquitetura
├── .gitignore
├── database/
│   ├── __init__.py
│   ├── db.py                      # Conexão, esquema e consultas SQLite
│   └── academic_motivation.db     # Banco local gerado/populado
├── models/
│   ├── __init__.py
│   └── assessment.py              # Modelo de domínio da avaliação
├── routes/
│   ├── __init__.py
│   ├── main_routes.py             # Dashboard e página Sobre
│   ├── assessment_routes.py       # Nova avaliação, resultado e detalhes
│   ├── dashboard_routes.py        # Histórico, dados simulados, validação e relatórios
│   └── api_routes.py              # API JSON para gráficos e atualização dinâmica
├── services/
│   ├── __init__.py
│   ├── text_processing.py         # Normalização, tokenização e stopwords
│   ├── sentiment_analysis.py      # Léxico simplificado e adaptador SentiLex-PT futuro
│   └── risk_calculation.py        # Regras, fatores e classificação configurável
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── new_assessment.html
│   ├── result.html
│   ├── history.html
│   ├── assessment_detail.html
│   ├── validation.html
│   ├── reports.html
│   ├── simulated_data.html
│   └── about.html
├── static/
│   ├── css/style.css
│   └── js/
│       ├── dashboard.js
│       └── assessment.js
├── data/
│   └── simulated_data.csv         # 300 registros explicitamente simulados
├── scripts/
│   ├── generate_simulated_data.py # Geração determinística do CSV sintético
│   └── seed_data.py               # Importação do CSV no SQLite
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_services.py
    └── test_routes.py
```

## 3. Modelo de banco de dados

A tabela principal `assessments` armazena dados acadêmicos, entrada textual e o resultado reproduzível da análise. Os termos encontrados são armazenados como JSON textual, o que preserva o detalhamento do resultado sem introduzir complexidade relacional prematura. Os índices de curso, semestre, risco e data apoiam filtros e agregações do dashboard.

| Campo | Tipo SQLite | Descrição |
|---|---|---|
| `id` | INTEGER, PK | Identificador da avaliação. |
| `course` | TEXT | Curso informado. |
| `semester` | INTEGER | Semestre entre 1 e 10. |
| `academic_workload` | TEXT | Percepção de carga acadêmica. |
| `difficulty` | TEXT | Percepção de dificuldade. |
| `satisfaction` | TEXT | Satisfação declarada com o curso. |
| `motivation` | TEXT | Motivação declarada para continuar. |
| `text_response` | TEXT | Resposta curta do estudante. |
| `text_polarity` | TEXT | Polaridade: `positive`, `neutral` ou `negative`. |
| `text_score` | INTEGER | Pontuação textual de risco, entre 0 e 2. |
| `positive_terms` | TEXT (JSON) | Termos positivos identificados. |
| `negative_terms` | TEXT (JSON) | Termos negativos identificados. |
| `contextual_score` | INTEGER | Pontuação contextual, entre 0 e 8. |
| `total_score` | INTEGER | Pontuação combinada, entre 0 e 10. |
| `risk_level` | TEXT | Nível computacional: Baixo, Médio ou Alto. |
| `expected_risk` | TEXT, nulo | Classe esperada, exclusiva para dados simulados. |
| `is_simulated` | INTEGER | Marca de dados sintéticos de validação. |
| `created_at` | TEXT | Data/hora UTC de criação. |

## 4. Fluxo funcional

O fluxo separa a orquestração HTTP da lógica de análise, tornando cada parte testável e substituível. Em uma versão futura, apenas o adaptador dentro de `sentiment_analysis.py` precisará ser substituído para incorporar o léxico SentiLex-PT ou um modelo como BERTimbau, preservando as rotas, o banco e a interface.

```text
Formulário da Nova Avaliação
          ↓
Validação dos campos na rota
          ↓
preprocess_text(texto)
          ↓
analyze_sentiment(texto processado)
          ↓
calculate_contextual_score(indicadores)
          ↓
calculate_text_score(polaridade)
          ↓
calculate_total_score(contexto, texto)
          ↓
calculate_risk_level(total)
          ↓
Geração dos fatores identificados
          ↓
Persistência no SQLite
          ↓
Página de resultado + atualização do dashboard
```

## 5. Regras iniciais de classificação

A pontuação contextual é calculada a partir das quatro respostas acadêmicas e pode atingir oito pontos. A análise lexical acrescenta de zero a dois pontos; assim, a pontuação total está limitada a dez. Os limiares de nível de risco permanecem centralizados em `config.py`, evitando valores dispersos pelo código.

| Faixa total | Classificação | Interpretação no sistema |
|---|---|---|
| 0–3 | Baixo risco | Indicadores computacionais reduzidos de desânimo acadêmico. |
| 4–6 | Médio risco | Indicadores computacionais que merecem acompanhamento acadêmico. |
| 7–10 | Alto risco | Conjunto de indicadores computacionais mais acentuado para acompanhamento pedagógico. |

A polaridade positiva equivale a 0 ponto textual, a neutra a 1 ponto e a negativa a 2 pontos. A primeira implementação emprega um léxico explícito, auditável e adequado para demonstração acadêmica. Ela não representa validação clínica, inferência diagnóstica ou avaliação individual de saúde.

## 6. Estratégia de validação

O conjunto `data/simulated_data.csv` contém 300 observações variadas e sintéticas: 100 esperadas como Baixo, 100 como Médio e 100 como Alto. A tela de validação compara a coluna `expected_risk` com o resultado calculado pelo sistema, produz acertos, erros, percentual de acerto e matriz de confusão. Por serem dados artificiais, a acurácia resultante mede somente a consistência da regra implementada sobre o cenário simulado; ela não comprova desempenho em uma população real.

## Referências

[1]: https://flask.palletsprojects.com/en/stable/ "Flask Documentation"
[2]: https://www.sqlite.org/docs.html "SQLite Documentation"
[3]: https://www.chartjs.org/docs/latest/ "Chart.js Documentation"
