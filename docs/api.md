# Documentação da API

## Visão Geral

Este documento descreve os principais componentes e funcionalidades da API do projeto mini-dolar-strategy.

## Índice

1. [Coleta de Dados](#coleta-de-dados)
2. [Análise Técnica](#análise-técnica)
3. [Análise de Sentimentos](#análise-de-sentimentos)
4. [Backtest](#backtest)
5. [Otimização](#otimização)
6. [Validação](#validação)
7. [Utilitários](#utilitários)

## Coleta de Dados

### `fetch_wdo_data(start_date: str, end_date: str) -> pd.DataFrame`

Coleta dados históricos do mini contrato de dólar (WDO).

```python
from src.data.collect_market_data import fetch_wdo_data

data = fetch_wdo_data('2023-01-01', '2023-12-31')
```

### `EconomicDataCollector`

Coleta indicadores econômicos relevantes.

```python
from src.data.economic_indicators import EconomicDataCollector

collector = EconomicDataCollector()
data = collector.collect_all_indicators('2023-01-01', '2023-12-31')
```

## Análise Técnica

### `calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame`

Calcula indicadores técnicos para análise.

```python
from src.models.technical_analysis import calculate_technical_indicators

df_with_indicators = calculate_technical_indicators(data)
```

## Análise de Sentimentos

### `NewsAnalyzer`

Analisa sentimentos de notícias relacionadas ao mercado.

```python
from src.models.sentiment_analysis import NewsAnalyzer

analyzer = NewsAnalyzer()
sentiment_df = analyzer.analyze_sentiment(news_data)
```

## Backtest

### `BacktestEngine`

Executa backtest da estratégia com diferentes configurações.

```python
from src.evaluation.backtesting import BacktestEngine

backtest = BacktestEngine(initial_capital=100000.0)
results = backtest.run_backtest(data, signals)
stats = backtest.get_statistics()
```

## Otimização

### `StrategyOptimizer`

Otimiza parâmetros da estratégia.

```python
from src.optimization.parameter_optimization import StrategyOptimizer

optimizer = StrategyOptimizer()
results = optimizer.optimize(
    data=data,
    strategy_class=TrendFollowingStrategy,
    parameter_grid={
        'short_window': [10, 20, 30],
        'long_window': [50, 100, 200]
    }
)
```

## Validação

### `TimeSeriesValidator`

Realiza validação cruzada adaptada para séries temporais.

```python
from src.evaluation.model_validation import TimeSeriesValidator

validator = TimeSeriesValidator(n_splits=5)
results = validator.validate_model(
    model=model,
    data=data,
    feature_columns=['Feature1', 'Feature2'],
    target_column='Target'
)
```

## Utilitários

### `StrategyLogger`

Configura logging para a aplicação.

```python
from src.utils.logging_config import StrategyLogger

logger = StrategyLogger().setup_logger('my_module')
```

### `StrategyMonitor`

Monitora e registra métricas da estratégia.

```python
from src.utils.logging_config import StrategyMonitor

monitor = StrategyMonitor()
monitor.record_metric('sharpe_ratio', 1.5)
```

## Interface de Linha de Comando (CLI)

### Comandos Disponíveis

```bash
# Coleta dados
python src/cli.py collect-data --days 252

# Executa backtest
python src/cli.py run-backtest --input-file data/market_data.csv

# Plota métricas
python src/cli.py plot-metrics --metric sharpe_ratio
```