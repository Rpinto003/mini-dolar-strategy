import pandas as pd
import sqlite3
from typing import Optional

class MT5DataLoader:
    def __init__(self, db_path: str):
        """
        Inicializa o carregador de dados do MT5
        
        Parameters:
        -----------
        db_path : str
            Caminho para o banco de dados SQLite
        """
        self.db_path = db_path
    
    def load_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Carrega dados do banco SQLite
        
        Parameters:
        -----------
        start_date : str, optional
            Data inicial no formato 'YYYY-MM-DD'
        end_date : str, optional
            Data final no formato 'YYYY-MM-DD'
        """
        try:
            # Construir a query SQL
            query = """
            SELECT 
                time as Date,
                open as Open,
                high as High,
                low as Low,
                close as Close,
                tick_volume as Volume,
                real_volume as RealVolume
            FROM candles
            """
            
            conditions = []
            if start_date:
                conditions.append(f"time >= '{start_date}'")
            if end_date:
                conditions.append(f"time <= '{end_date}'")
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += " ORDER BY time"
            
            # Conectar ao banco e carregar dados
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn)
                
                if df.empty:
                    raise ValueError("No data returned from database")
                
                # Converter coluna de data para datetime
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
                
                # Converter colunas numéricas
                numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'RealVolume']
                for col in numeric_columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Remover linhas com valores ausentes
                df = df.dropna()
                
                print(f"Data loaded successfully. Shape: {df.shape}")
                return df
                
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            raise

    def get_available_dates(self) -> tuple:
        """Retorna a primeira e última data disponível no banco"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT MIN(time), MAX(time) FROM candles")
                min_date, max_date = cursor.fetchone()
                return min_date, max_date
        except Exception as e:
            print(f"Error getting dates: {str(e)}")
            return None, None