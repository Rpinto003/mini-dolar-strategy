import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import logging
import os
from pathlib import Path

class MarketDataLoader:
    def __init__(self, db_path: str = None):
        """Inicializa o carregador de dados de mercado.
        
        Args:
            db_path: Caminho para o arquivo .db. Se None, usará o path padrão.
        """
        self.logger = logging.getLogger(__name__)
        
        # Define path padrão se não fornecido
        if db_path is None:
            db_path = os.path.join(
                Path(__file__).parent,
                'candles.db'
            )
            
        self.db_path = db_path
        self.logger.info(f"Usando banco de dados: {self.db_path}")
        
        # Verifica se o arquivo existe
        if not os.path.exists(self.db_path):
            self.logger.warning(f"Arquivo de banco de dados não encontrado: {self.db_path}")
    
    def load_data(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Carrega dados do banco SQLite.
        
        Args:
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)
            
        Returns:
            DataFrame com dados OHLCV
        """
        try:
            query = "SELECT * FROM candles"
            conditions = []
            
            if start_date:
                conditions.append(f"time >= '{start_date}'")
            if end_date:
                conditions.append(f"time <= '{end_date}'")
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += " ORDER BY time ASC"
            
            # Conecta ao banco e lê os dados
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, parse_dates=['time'])
                
            df.set_index('time', inplace=True)
            self.logger.info(f"Dados carregados: {len(df)} registros")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados: {str(e)}")
            return pd.DataFrame()
    
    def get_daily_data(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Retorna dados diários (agregação de candles intraday).
        
        Args:
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)
            
        Returns:
            DataFrame com dados OHLCV diários
        """
        df = self.load_data(start_date, end_date)
        if df.empty:
            return df
            
        # Agrupa por dia
        daily_data = pd.DataFrame()
        daily_data['open'] = df['open'].resample('D').first()
        daily_data['high'] = df['high'].resample('D').max()
        daily_data['low'] = df['low'].resample('D').min()
        daily_data['close'] = df['close'].resample('D').last()
        daily_data['volume'] = df['real_volume'].resample('D').sum()
        
        return daily_data.dropna()
    
    def get_minute_data(self, interval: int = 1,
                        start_date: str = None,
                        end_date: str = None) -> pd.DataFrame:
        """Retorna dados em intervalos de minutos específicos.
        
        Args:
            interval: Intervalo em minutos (1, 5, 15, etc)
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)
            
        Returns:
            DataFrame com dados OHLCV no intervalo especificado
        """
        df = self.load_data(start_date, end_date)
        if df.empty:
            return df
            
        # Resampling para o intervalo desejado
        rule = f"{interval}T"
        resampled_data = pd.DataFrame()
        resampled_data['open'] = df['open'].resample(rule).first()
        resampled_data['high'] = df['high'].resample(rule).max()
        resampled_data['low'] = df['low'].resample(rule).min()
        resampled_data['close'] = df['close'].resample(rule).last()
        resampled_data['volume'] = df['real_volume'].resample(rule).sum()
        
        return resampled_data.dropna()
    
    def get_trading_sessions(self, data: pd.DataFrame) -> pd.DataFrame:
        """Identifica sessões de trading nos dados.
        
        Args:
            data: DataFrame com dados OHLCV
            
        Returns:
            DataFrame com sessões identificadas
        """
        df = data.copy()
        
        # Adiciona informações de sessão
        df['session'] = 'regular'
        df.loc[df.index.hour < 9, 'session'] = 'pre_market'
        df.loc[df.index.hour >= 17, 'session'] = 'after_market'
        
        # Marca horário de almoço
        df.loc[(df.index.hour == 12) | 
               (df.index.hour == 13), 'session'] = 'lunch'
        
        return df

def main():
    """Função principal para teste."""
    # Configura logging
    logging.basicConfig(level=logging.INFO)
    
    # Testa carregamento de dados
    loader = MarketDataLoader()
    
    # Testa diferentes intervalos
    intervals = [1, 5, 15, 60]  # 1min, 5min, 15min, 1h
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5)
    
    for interval in intervals:
        data = loader.get_minute_data(
            interval=interval,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        if not data.empty:
            print(f"\nDados {interval}min:")
            print(data.head())
            
    # Testa dados diários
    daily_data = loader.get_daily_data(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    
    if not daily_data.empty:
        print("\nDados diários:")
        print(daily_data.head())

if __name__ == '__main__':
    main()