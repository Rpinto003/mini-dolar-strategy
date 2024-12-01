from .feature_engineering import FeatureEngineer
import pandas as pd
import numpy as np

class DataProcessor:
    """Classe responsável pelo processamento dos dados"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.feature_engineer = FeatureEngineer(data)
    
    def prepare_features(self) -> pd.DataFrame:
        """Prepara todas as features para o modelo"""
        print("Creating technical features...")
        technical = self.feature_engineer.create_technical_features()
        print(f"Technical features shape: {technical.shape}")
        
        print("Creating volume features...")
        volume = self.feature_engineer.create_volume_features()
        print(f"Volume features shape: {volume.shape}")
        
        print("Creating time features...")
        time = self.feature_engineer.create_time_features()
        print(f"Time features shape: {time.shape}")
        
        print("Concatenating features...")
        features = pd.concat([technical, volume, time], axis=1)
        print(f"Combined features shape before cleaning: {features.shape}")
        
        cleaned_features = self._clean_data(features)
        print(f"Final features shape after cleaning: {cleaned_features.shape}")
        
        return cleaned_features
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpa e prepara os dados"""
        df = df.replace([np.inf, -np.inf], np.nan)
        return df.dropna()