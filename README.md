# Sistema de Detecção de Desânimo Acadêmico

**Projeto-base para Trabalho de Conclusão de Curso em Ciência da Computação.** Esta aplicação web local registra indicadores do contexto acadêmico e respostas textuais curtas, realizando uma classificação computacional em **Baixo**, **Médio** ou **Alto risco** de desânimo acadêmico. O objetivo é oferecer uma base organizada, explicável e evolutiva para acompanhamento acadêmico.

> **Aviso de escopo:** o sistema **não realiza diagnóstico psicológico, clínico ou médico**. Os resultados são indicadores computacionais baseados em dados contextuais e respostas textuais, destinados exclusivamente ao apoio do acompanhamento acadêmico.

## Visão geral

A aplicação utiliza regras transparentes de pontuação. A resposta textual passa por normalização, tokenização e remoção de stopwords; em seguida, um léxico inicial em português identifica termos positivos e negativos. Os quatro indicadores acadêmicos são pontuados separadamente e combinados com a contribuição textual. A arquitetura foi organizada para que o léxico simplificado seja futuramente substituído por SentiLex-PT ou por modelos mais avançados, como BERTimbau, sem reescrever as rotas ou a interface.

| Componente | Escolha | Finalidade |
|---|---|---|
| Backend | Python 3 + Flask | Rotas, validação, templates e integração do fluxo. |
| Banco de dados | SQLite | Persistência local em um único arquivo. |
| Frontend | HTML, CSS, JavaScript, Bootstrap 5 | Interface responsiva e acadêmica. |
| Gráficos | Chart.js | Visualização de distribuição e tendências no dashboard. |
| PLN inicial | Léxico PT-BR auditável | Polaridade e termos encontrados. |
| Testes | Pytest + cliente Flask | Cobertura de serviços e rotas principais. |

A documentação oficial do Flask contempla roteamento, renderização de templates, testes e padrões de uso do SQLite em aplicações web locais. [1] SQLite é apropriado para a primeira versão por sua persistência baseada em arquivo e ampla documentação de SQL. [2] Chart.js oferece os tipos de gráficos em canvas utilizados pelo dashboard. [3]

## Arquitetura e fluxo

O arquivo [ARCHITECTURE.md](ARCHITECTURE.md) apresenta a arquitetura escolhida, a árvore completa de pastas, o modelo de dados e o fluxo do sistema antes da implementação. De forma resumida, as rotas recebem e validam os dados; os serviços processam texto, calculam a polaridade e aplicam as regras de risco; o modelo representa o registro; e o módulo SQLite persiste o resultado.

```text
Entrada do formulário
        ↓
Validação da rota
        ↓
Pré-processamento de texto
        ↓
Análise de polaridade lexical
        ↓
Pontuação contextual + textual
        ↓
Classificação de risco
        ↓
Armazenamento em SQLite
        ↓
Resultado, histórico, dashboard e relatórios
```

## Estrutura de pastas

```text
sistema-desanimo-academico-flask/
├── app.py
├── config.py
├── requirements.txt
├── ARCHITECTURE.md
├── README.md
├── database/                 # Conexão, esquema e banco SQLite
├── models/                   # Entidade Assessment
├── services/                 # Texto, sentimento, risco e carga de dados
├── routes/                   # Blueprints da aplicação e API JSON
├── templates/                # Páginas Jinja/HTML
├── static/                   # CSS e JavaScript
├── data/                     # CSV com 300 dados simulados
├── scripts/                  # Geração e carga do conjunto sintético
└── tests/                    # Testes automatizados
```

## Requisitos

É necessário ter **Python 3.10 ou superior** e `pip` instalados. O projeto foi desenvolvido para executar localmente sem serviços externos, exceto pelos CDNs de Bootstrap e Chart.js utilizados apenas para estilo e gráficos. Para uso inteiramente offline, esses arquivos podem ser baixados e servidos em `static/` futuramente.

## Instalação

No terminal, entre na pasta do projeto e crie um ambiente virtual:

```bash
cd sistema-desanimo-academico-flask
python3 -m venv .venv
source .venv/bin/activate
```

No Windows PowerShell, ative com:

```powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Geração do banco e dados simulados

O arquivo `data/simulated_data.csv` já acompanha o projeto e contém **300 registros explicitamente simulados para fins de validação**. Ao executar a aplicação pela primeira vez, o banco `database/academic_motivation.db` é criado automaticamente e os dados sintéticos são carregados caso a tabela esteja vazia.

Caso seja necessário gerar novamente o arquivo CSV de modo determinístico, execute:

```bash
python scripts/generate_simulated_data.py
```

Para substituir somente os registros simulados armazenados no banco, execute:

```bash
python scripts/seed_data.py --replace
```

Registros criados manualmente pela tela **Nova Avaliação** não são removidos por esse comando.

## Execução

Com o ambiente virtual ativo, inicie a aplicação:

```bash
python app.py
```

Em um ambiente diferente de desenvolvimento, defina `SECRET_KEY` por variável de ambiente antes de iniciar o Flask; o valor embutido no código serve apenas para a execução local do protótipo.

Acesse no navegador:

```text
http://127.0.0.1:5000
```

Alternativamente, o servidor Flask pode ser iniciado pela CLI:

```bash
flask --app app run --debug
```

## Como utilizar

A navegação lateral reúne todas as funcionalidades. O **Dashboard** mostra cartões dinâmicos, quatro gráficos e registros recentes. Em **Nova Avaliação**, informe curso, semestre, carga, dificuldade, satisfação, motivação e uma resposta textual de até mil caracteres. Após a análise, a página de resultado apresenta polaridade, pontuações, nível de risco e fatores considerados.

O **Histórico** disponibiliza busca e filtros por curso, semestre e risco. A página de **Dados Simulados** explica a origem do conjunto sintético e permite recarregá-lo. **Validação** compara a classificação esperada do CSV com a classificação produzida, informando acurácia e matriz de confusão. Em **Relatórios**, o resumo pode ser exportado em CSV.

## Regras de classificação

As regras iniciais são concentradas em `services/risk_calculation.py`; os limiares podem ser modificados exclusivamente em `config.py`.

| Indicador contextual | 0 ponto | 1 ponto | 2 pontos |
|---|---|---|---|
| Carga acadêmica | Muito baixa, Baixa | Moderada | Alta, Muito alta |
| Dificuldade | Muito baixa, Baixa | Moderada | Alta, Muito alta |
| Satisfação | Muito satisfeito, Satisfeito | Neutro | Insatisfeito, Muito insatisfeito |
| Motivação | Muito alta, Alta | Moderada | Baixa, Muito baixa |

| Polaridade textual | Pontos de risco |
|---|---:|
| Positiva | 0 |
| Neutra | 1 |
| Negativa | 2 |

| Pontuação total | Classificação computacional |
|---:|---|
| 0–3 | Baixo risco |
| 4–6 | Médio risco |
| 7–10 | Alto risco |

## Testes automatizados

Execute a suíte de testes com:

```bash
pytest -q
```

Os testes verificam normalização do texto, análise de sentimento, limites das regras de risco, persistência de uma avaliação, validação do formulário e agregados da API do dashboard.

## Limitações e evolução prevista

A análise de sentimentos desta primeira versão é deliberadamente lexical e baseada em termos explícitos. Ela não compreende contexto complexo, ironia, ambiguidade, negação em todas as situações ou variações linguísticas extensas. Por isso, o resultado deve ser interpretado como um indicador técnico de apoio, jamais como avaliação pessoal definitiva ou diagnóstico.

As evoluções adequadas incluem a integração de SentiLex-PT no adaptador de `services/sentiment_analysis.py`, avaliações metodológicas com conjunto de dados autorizado e anonimizado, melhoria das métricas, controle de acesso, auditoria, consentimento informado e exportação de relatórios em PDF. Qualquer uso com dados reais deve observar requisitos institucionais, éticos, de privacidade e de proteção de dados aplicáveis.

## Referências

[1]: https://flask.palletsprojects.com/en/stable/ "Flask Documentation"
[2]: https://www.sqlite.org/docs.html "SQLite Documentation"
[3]: https://www.chartjs.org/docs/latest/ "Chart.js Documentation"
