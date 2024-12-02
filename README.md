# Mini Dólar (WDO) Trading Strategy

## Projeto de Machine Learning para Análise de Preços dos Contratos de WDO

Este projeto combina análise técnica e fundamentalista usando machine learning para prever preços dos mini contratos de dólar (WDO).

## Estrutura do Projeto

```
├── data/
│   ├── raw/                 # Dados brutos coletados
│   ├── processed/           # Dados processados para análise
│   └── external/            # Dados externos (indicadores econômicos, etc)
├── notebooks/              # Jupyter notebooks para análise e experimentação
├── src/
│   ├── data/               # Scripts para coleta e processamento de dados
│   ├── features/           # Scripts para engenharia de features
│   ├── models/             # Implementação dos modelos
│   └── visualization/      # Scripts para visualização
├── tests/                  # Testes unitários
├── config/                 # Arquivos de configuração
└── requirements.txt        # Dependências do projeto
```

## Componentes Principais

1. **Análise Fundamentalista**
   - Coleta de dados econômicos e financeiros
   - Análise de sentimentos de notícias usando NLP
   - Integração com indicadores macroeconômicos

2. **Análise Técnica**
   - Processamento de dados históricos
   - Implementação de indicadores técnicos
   - Identificação de padrões de preço

3. **Modelo Integrado**
   - Combinação de análises técnica e fundamentalista
   - Pipeline de previsão de preços
   - Validação e backtesting

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

[Em desenvolvimento]

## Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

[MIT](LICENSE)
