# Enhanced Mini-Dólar Trading Strategy

Este projeto implementa uma estratégia avançada de trading para o mini contrato de dólar (WDO) utilizando uma combinação de machine learning e análise técnica.

## Características Principais

### 1. Análise de Contexto de Mercado
- Identificação de horários importantes (9h-10h, 10:30-11:30, 15h-16h)
- Volume Profile e Point of Control (POC)
- Referências do dia anterior

### 2. Indicadores Técnicos Avançados
- EMAs adaptativas (9 e 21 períodos)
- RSI com detecção de divergências
- ATR para análise de volatilidade
- Bandas de Bollinger
- Análise de volume relativo

### 3. Sistema de Sinais Combinados
- Scalping em tendência forte
- Reversão em extremos com confirmação
- Breakout de ranges

### 4. Gestão de Risco Dinâmica
- Sizing baseado em volatilidade
- Stop loss adaptativo
- Filtros de volume e volatilidade

### 5. Machine Learning Otimizado
- Random Forest Classifier
- Features selecionadas especificamente para WDO
- Normalização adaptativa dos dados

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/Rpinto003/mini-dolar-strategy.git
cd mini-dolar-strategy
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Instale o TA-Lib:
Windows:
```bash
pip install TA-Lib
```
Linux:
```bash
sudo apt-get update
sudo apt-get install ta-lib
pip install TA-Lib
```

## Configuração

1. Ajuste o caminho do banco de dados em `main.py`:
```python
db_path = "caminho/para/seu/banco/candles.db"
```

2. Configure os parâmetros da estratégia em `enhanced_strategy.py` conforme necessário.

## Uso

1. Execute a estratégia:
```bash
python main.py
```

2. Analise os resultados nos gráficos e métricas gerados.

## Estrutura do Projeto

- `main.py`: Ponto de entrada do programa
- `enhanced_strategy.py`: Implementação da estratégia avançada
- `backtest.py`: Sistema de backtest
- `data.py`: Carregamento e processamento de dados
- `analysis.py`: Análise de performance

## Notas Importantes

1. Horários de Operação
   - A estratégia opera principalmente durante o horário comercial (9h-17h)
   - Evita operações no horário de almoço (12h-13h)

2. Gestão de Risco
   - Tamanho máximo da posição: 2 contratos
   - Stop loss dinâmico baseado em ATR
   - Filtros de volume e volatilidade

## Contribuições

Contribuições são bem-vindas! Por favor, sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a licença MIT.
