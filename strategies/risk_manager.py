# strategies/risk_manager.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class RiskManager:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        # Parâmetros de risco
        self.max_trades = 3           # Máximo de trades simultâneos
        self.stop_loss_atr = 2.0      # Stop loss em múltiplos de ATR
        self.take_profit_atr = 4.0    # Take profit em múltiplos de ATR
        self.max_drawdown = 0.10      # Máximo drawdown permitido (10%)
        
    def calculate_atr(self, window: int = 14) -> pd.Series:
        """Calcula o Average True Range"""
        high = self.data['High']
        low = self.data['Low']
        close = self.data['Close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        return tr.rolling(window=window).mean()
    
    def apply_risk_management(self, signals: pd.Series) -> pd.Series:
        """Aplica regras de gestão de risco aos sinais"""
        risk_adjusted_signals = signals.copy()
        
        # Calcular ATR
        atr = self.calculate_atr()
        
        # Controle de trades simultâneos
        active_trades = signals.abs().rolling(window=5).sum()
        risk_adjusted_signals[active_trades > self.max_trades] = 0
        
        # Aplicar stops dinâmicos
        close = self.data['Close']
        for i in range(len(signals)):
            if signals.iloc[i] != 0:  # Nova posição
                entry_price = close.iloc[i]
                position_type = signals.iloc[i]  # 1 para long, -1 para short
                
                # Calcular níveis de stop e take profit
                atr_value = atr.iloc[i]
                stop_loss = entry_price - (position_type * self.stop_loss_atr * atr_value)
                take_profit = entry_price + (position_type * self.take_profit_atr * atr_value)
                
                # Verificar próximos candles
                for j in range(i+1, len(signals)):
                    current_price = close.iloc[j]
                    
                    # Verificar stop loss
                    if (position_type == 1 and current_price < stop_loss) or \
                       (position_type == -1 and current_price > stop_loss):
                        risk_adjusted_signals.iloc[j] = -position_type  # Fechar posição
                        break
                    
                    # Verificar take profit
                    if (position_type == 1 and current_price > take_profit) or \
                       (position_type == -1 and current_price < take_profit):
                        risk_adjusted_signals.iloc[j] = -position_type  # Fechar posição
                        break
        
        return risk_adjusted_signals
    
    def check_drawdown(self, equity: pd.Series) -> bool:
        """Verifica se o drawdown máximo foi atingido"""
        if len(equity) < 2:
            return True
            
        peak = equity.expanding().max()
        drawdown = (equity - peak) / peak
        
        return drawdown.min() > -self.max_drawdown