# Mini Dólar Strategy

Este projeto implementa estratégias de trading para mini contratos de dólar.

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

```python
from strategies import MeanReversionStrategy
from backtest import Backtester

# Criar estratégia
strategy = MeanReversionStrategy(data, risk_manager)

# Executar backtest
backtester = Backtester(strategy)
results = backtester.run()
```