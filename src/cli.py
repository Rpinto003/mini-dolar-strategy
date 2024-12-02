import click
import pandas as pd
from datetime import datetime, timedelta
from src.data.collect_market_data import fetch_wdo_data
from src.models.technical_analysis import calculate_technical_indicators
from src.models.sentiment_analysis import NewsAnalyzer
from src.evaluation.backtesting import BacktestEngine
from src.utils.logging_config import StrategyLogger, StrategyMonitor

# Configura logging
logger = StrategyLogger().setup_logger('cli')
monitor = StrategyMonitor()

@click.group()
def cli():
    """Ferramenta de linha de comando para estratégia de WDO."""
    pass

@cli.command()
@click.option('--days', default=252, help='Número de dias para coletar')
@click.option('--output', default='data/raw/market_data.csv',
              help='Arquivo de saída')
def collect_data(days, output):
    """Coleta dados históricos do WDO."""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        logger.info(f"Coletando dados de {start_date} até {end_date}")
        
        data = fetch_wdo_data(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        data.to_csv(output)
        logger.info(f"Dados salvos em {output}")
        
    except Exception as e:
        logger.error(f"Erro ao coletar dados: {str(e)}")
        raise click.ClickException(str(e))

@cli.command()
@click.option('--input-file', required=True,
              help='Arquivo com dados de mercado')
@click.option('--output-file', default='results/backtest_results.csv',
              help='Arquivo para resultados do backtest')
def run_backtest(input_file, output_file):
    """Executa backtest da estratégia."""
    try:
        logger.info("Iniciando backtest")
        
        # Carrega dados
        data = pd.read_csv(input_file, index_col=0, parse_dates=True)
        
        # Calcula indicadores
        data = calculate_technical_indicators(data)
        
        # Executa backtest
        backtest = BacktestEngine()
        results = backtest.run_backtest(data, data['Signal'])
        
        # Salva resultados
        results.to_csv(output_file)
        
        # Registra métricas
        stats = backtest.get_statistics()
        for metric, value in stats.items():
            monitor.record_metric(metric, value)
            
        logger.info(f"Backtest concluído. Resultados salvos em {output_file}")
        
    except Exception as e:
        logger.error(f"Erro ao executar backtest: {str(e)}")
        raise click.ClickException(str(e))

@cli.command()
@click.option('--metric', required=True,
              help='Nome da métrica para visualizar')
def plot_metrics(metric):
    """Plota evolução de uma métrica."""
    try:
        monitor.plot_metric(metric)
    except Exception as e:
        logger.error(f"Erro ao plotar métrica: {str(e)}")
        raise click.ClickException(str(e))

if __name__ == '__main__':
    cli()