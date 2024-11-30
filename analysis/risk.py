import pandas as pd
import numpy as np
from typing import Dict

class RiskAnalyzer:
    def __init__(self, results: pd.DataFrame):
        self.results = results
    
    def calculate_risk_metrics(self) -> Dict:
        metrics = {
            'volatility': self._calculate_volatility(),
            'var': self._calculate_var(),
            'sharpe': self._calculate_sharpe()
        }
        return metrics