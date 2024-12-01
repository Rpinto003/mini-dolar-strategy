import pandas as pd
import numpy as np
from typing import Dict
import traceback

class Backtester:
    def __init__(self, strategy, initial_capital: float = 100000.0):
        self.strategy = strategy
        self.initial_capital = initial_capital
        
    def run(self) -> pd.DataFrame:
        """Execute backtest and return results"""
        try:
            # Generate signals
            signals = self.strategy.generate_signals()
            print(f"Signals generated: {signals.shape}")
            
            # Ensure signals align with data index
            signals = signals.reindex(self.strategy.data.index).fillna(0)
            
            # Initialize portfolio
            portfolio = pd.DataFrame(index=self.strategy.data.index)
            portfolio['position'] = signals
            portfolio['close'] = self.strategy.data['Close']
            
            # Calculate returns
            portfolio['returns'] = portfolio['close'].pct_change().fillna(0)
            portfolio['strategy_returns'] = portfolio['position'].shift(1).fillna(0) * portfolio['returns']
            
            # Add transaction costs (0.02% per trade)
            portfolio['trades'] = portfolio['position'].diff().abs().fillna(0)
            portfolio['costs'] = portfolio['trades'] * 0.0002
            portfolio['strategy_returns'] = portfolio['strategy_returns'] - portfolio['costs']
            
            # Calculate equity curve
            portfolio['equity'] = self.initial_capital * (1 + portfolio['strategy_returns']).cumprod()
            
            return portfolio
            
        except Exception as e:
            print(f"Erro no backtest: {str(e)}")
            traceback.print_exc()
            return pd.DataFrame()
