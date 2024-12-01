import pandas as pd
import numpy as np
from typing import List, Dict

class FeatureEngineer:
    """Classe responsável pela criação de features"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        
    def create_technical_features(self) -> pd.DataFrame:
        """Cria features baseadas em indicadores técnicos"""
        df = pd.DataFrame(index=self.data.index)
        
        # Preços e retornos
        df['returns'] = self.data['Close'].pct_change()
        df['log_returns'] = np.log(self.data['Close']).diff()
        
        # Features técnicas
        for window in [5, 15, 30, 60]:
            df[f'sma_{window}'] = self.data['Close'].rolling(window).mean()
            df[f'momentum_{window}'] = self.data['Close'].pct_change(window)
            df[f'volatility_{window}'] = df['returns'].rolling(window).std()
        
        return df
    
    def create_volume_features(self) -> pd.DataFrame:
        """Cria features baseadas em volume"""
        df = pd.DataFrame(index=self.data.index)
        
        df['volume'] = self.data['Volume']
        df['volume_ma'] = df['volume'].rolling(20).mean()
        df['volume_std'] = df['volume'].rolling(20).std()
        
        return df
    
    def create_time_features(self) -> pd.DataFrame:
        """Cria features baseadas em tempo"""
        df = pd.DataFrame(index=self.data.index)
        
        df['hour'] = self.data.index.hour
        df['minute'] = self.data.index.minute
        df['day_of_week'] = self.data.index.dayofweek
        
        return df