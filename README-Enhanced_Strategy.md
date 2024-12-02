### Documentação - Enhanced WDO Strategy
## Visão Geral
A Enhanced WDO Strategy é uma estratégia avançada para trading de mini contratos de dólar (WDO) que combina análise técnica tradicional, análise de contexto de mercado e machine learning. A estratégia foi projetada para capturar diferentes tipos de movimentos do mercado enquanto mantém uma gestão de risco rigorosa.
## Componentes Principais
## 1. Análise de Contexto de Mercado
# Filtros de Horário

Foco nos horários de maior liquidez (9h-16h)
Evita operações no horário de almoço (12h-13h)
Identificação de horários-chave (9h, 10h, 15h, 16h) devido a:

Abertura do mercado
Divulgações econômicas
Maior volume de negociação



# Volume Profile

Cálculo do Point of Control (POC) diário
Identificação de níveis de suporte/resistência baseados em volume
Análise de desvios do preço em relação ao POC
Auxilia na identificação de áreas de valor e extremos

# Dados do Dia Anterior

Referências de preço (máxima, mínima, fechamento)
Auxilia na identificação de níveis importantes
Serve como base para cálculos de volatilidade relativa

## 2. Indicadores Técnicos
# Tendência

EMAs adaptativas (9 e 21 períodos)
Força da tendência baseada na diferença entre EMAs
Filtro de qualidade da tendência

# Momentum

RSI com período de 14
Detecção de divergências
Identificação de sobrecompra/sobrevenda

# Volatilidade

ATR (Average True Range)
Bandas de Bollinger
Ajuste dinâmico de stops e targets

# Volume

Média móvel de volume (20 períodos)
Ratio de volume atual/média
Filtro de liquidez mínima

## 3. Sistema de Sinais
# Estratégias Base

# Scalping em Tendência

Requer tendência definida
Volume acima da média
RSI em zona neutra


# Reversão em Extremos

Divergências confirmadas
Volume aumentado
Níveis técnicos importantes


# Breakout

Rompimento do POC
Volume muito acima da média
Volatilidade controlada



# Combinação de Sinais

Ponderação das diferentes estratégias
Confirmação cruzada entre indicadores
Filtros de qualidade do sinal

## 4. Machine Learning
# Modelo

Random Forest Classifier
200 árvores de decisão
Otimizado para reduzir overfitting

## Features

# Técnicas

Força da tendência
RSI
Ratio de volume
Desvio do POC
ATR


# Contextuais

Horários-chave
Dados do dia anterior
Métricas de volatilidade



# Processo de Treinamento

Divisão treino/teste (70/30)
Normalização adaptativa
Validação temporal
Labels baseados em retornos futuros

## 5. Gestão de Risco
Sizing Dinâmico

Base: 1 contrato
Ajuste por volatilidade (ATR)
Limites: 0.5 a 2 contratos
Correlação com volume

# Stops

Dinâmicos baseados em ATR
Típicamente 1.5x ATR
Ajuste por volatilidade do dia

# Filtros de Risco

Volume mínimo requerido
Volatilidade excessiva
Horários inadequados

## 6. Monitoramento e Ajustes
# Métricas Principais

Sharpe Ratio
Drawdown máximo
Fator de lucro
Taxa de acerto
Retorno por volatilidade

# Ajustes Dinâmicos

Calibração de parâmetros
Ajuste de filtros
Otimização de sizing

# Pontos Críticos
# Vantagens

Abordagem multi-estratégia
Gestão de risco robusta
Adaptação a diferentes condições de mercado
Uso de múltiplas confirmações

# Limitações

Dependência de volume e liquidez
Necessidade de dados de qualidade
Períodos iniciais sem operação (warmup)
Custo computacional significativo

# Considerações Operacionais
# Implementação

Preparação de dados históricos
Cálculo prévio de indicadores
Treinamento do modelo
Execução do backtest
Análise de resultados

# Manutenção

Recalibração periódica
Monitoramento de performance
Ajustes de parâmetros
Validação contínua

## Recomendações Futuras
# Melhorias Potenciais

Inclusão de dados fundamentais
Otimização de hiperparâmetros
Implementação de ensemble de modelos
Análise de correlação com outros mercados

# Expansões Possíveis

Adaptação para outros contratos
Integração com análise fundamentalista
Desenvolvimento de versão intraday
Implementação de execução automática