import pandas as pd
from typing import Dict

class Backtester:
    def __init__(self, strategy, initial_capital: float = 100000.0):
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.positions = []
    
    def run(self) -> Dict:
        signals = self.strategy.generate_signals()
        results = self._calculate_returns(signals)
        return self._calculate_metrics(results)