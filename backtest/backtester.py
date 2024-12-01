# backtest/backtester.py
import pandas as pd
import numpy as np
from typing import Dict

class Backtester:
    def __init__(self, strategy, initial_capital: float = 100000.0):
        """
        Inicializa o backtester
        
        Parameters:
        -----------
        strategy : BaseStrategy
            Estratégia de trading a ser testada
        initial_capital : float, optional (default=100000.0)
            Capital inicial para o backtest
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        
    def run(self) -> Dict:
        """Execute backtest and return results"""
        try:
            # Generate signals
            signals = self.strategy.generate_signals()
            
            # Initialize portfolio
            portfolio = pd.DataFrame(index=self.strategy.data.index)
            portfolio['position'] = signals
            portfolio['close'] = self.strategy.data['Close']
            
            # Calculate returns
            portfolio['returns'] = portfolio['close'].pct_change().fillna(0)
            portfolio['strategy_returns'] = portfolio['position'].shift(1) * portfolio['returns']
            
            # Add transaction costs (0.02% per trade)
            portfolio['trades'] = portfolio['position'].diff().abs()
            portfolio['costs'] = portfolio['trades'] * 0.0002
            portfolio['strategy_returns'] = portfolio['strategy_returns'] - portfolio['costs']
            
            # Calculate equity curve
            portfolio['equity'] = self.initial_capital * (1 + portfolio['strategy_returns']).cumprod()
            
            return portfolio
            
        except Exception as e:
            print(f"Erro no backtest: {str(e)}")
            return pd.DataFrame()