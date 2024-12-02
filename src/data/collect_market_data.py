import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def fetch_wdo_data(start_date: str, end_date: str) -> pd.DataFrame:
    """Coleta dados históricos do mini dólar (WDO).
    
    Args:
        start_date (str): Data inicial no formato 'YYYY-MM-DD'
        end_date (str): Data final no formato 'YYYY-MM-DD'
        
    Returns:
        pd.DataFrame: DataFrame com dados OHLCV do WDO
    """
    try:
        # Por enquanto, usamos o USD/BRL como proxy
        ticker = 'BRL=X'
        df = yf.download(ticker, start=start_date, end=end_date)
        
        if df.empty:
            logger.warning(f"Nenhum dado encontrado para o período {start_date} a {end_date}")
            return pd.DataFrame()
            
        logger.info(f"Dados coletados com sucesso: {len(df)} registros")
        return df
        
    except Exception as e:
        logger.error(f"Erro ao coletar dados do WDO: {str(e)}")
        return pd.DataFrame()

def main():
    """Função principal para teste."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    data = fetch_wdo_data(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    
    if not data.empty:
        print("\nDados coletados:")
        print(data.head())
    
if __name__ == '__main__':
    main()