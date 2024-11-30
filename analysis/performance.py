import pandas as pd
import numpy as np
from typing import Dict

class PerformanceAnalyzer:
    def __init__(self, results: pd.DataFrame):
        self.results = results
    
    def calculate_metrics(self) -> Dict:
        metrics = {
            'total_return': self._calculate_total_return(),
            'sharpe_ratio': self._calculate_sharpe_ratio(),
            'max_drawdown': self._calculate_max_drawdown()
        }
        return metrics