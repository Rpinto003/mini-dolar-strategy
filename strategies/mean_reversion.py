from .base_strategy import BaseStrategy
import pandas as pd
import numpy as np

class MeanReversionStrategy(BaseStrategy):
    def __init__(self, data: pd.DataFrame, risk_manager, lookback: int = 20):
        super().__init__(data, risk_manager)
        self.lookback = lookback
        
    def generate_signals(self) -> pd.Series:
        mean = self.data['close'].rolling(window=self.lookback).mean()
        std = self.data['close'].rolling(window=self.lookback).std()
        z_score = (self.data['close'] - mean) / std
        signals = pd.Series(index=self.data.index, data=0)
        signals[z_score > 1] = -1
        signals[z_score < -1] = 1
        return signals