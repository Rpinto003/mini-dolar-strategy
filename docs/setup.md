# Configuração do Ambiente

## Requisitos

- Python 3.8+
- pip
- Git

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/Rpinto003/mini-dolar-strategy.git
cd mini-dolar-strategy
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Estrutura do Projeto

```
mini-dolar-strategy/
├── data/               # Dados brutos e processados
├── docs/               # Documentação
├── logs/               # Arquivos de log
├── notebooks/          # Jupyter notebooks
├── results/            # Resultados e relatórios
├── src/                # Código fonte
├── tests/              # Testes unitários
├── requirements.txt    # Dependências
└── README.md           # Documentação principal
```

## Configuração

1. Configure as variáveis de ambiente no arquivo `.env`:
```
API_KEY=sua_chave_api
LOG_LEVEL=INFO
```

2. Crie os diretórios necessários:
```bash
mkdir -p data/{raw,processed} logs results
```

## Execução dos Testes

```bash
python -m pytest tests/
```

## Uso Básico

1. Coleta de dados:
```bash
python src/cli.py collect-data --days 252
```

2. Execução do backtest:
```bash
python src/cli.py run-backtest --input-file data/raw/market_data.csv
```

3. Visualização de resultados:
```bash
python src/cli.py plot-metrics --metric sharpe_ratio
```