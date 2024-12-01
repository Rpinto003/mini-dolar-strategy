# strategies/mean_reversion.py
from .base_strategy import BaseStrategy
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from .risk_manager import RiskManager

class MeanReversionStrategy(BaseStrategy):
    def generate_signals(self) -> pd.Series:
        # Inicializar sinais com zeros
        signals = pd.Series(0, index=self.data.index)
        
        # Garantir que estamos trabalhando com séries unidimensionais
        close = self.data['Close'].squeeze()
        
        # Calcular indicadores
        sma_20 = close.rolling(window=20).mean()
        std_20 = close.rolling(window=20).std()
        
        # Calcular bandas
        upper_band = sma_20 + (2 * std_20)
        lower_band = sma_20 - (2 * std_20)
        
        # Criar máscaras para os sinais
        buy_mask = close < lower_band
        sell_mask = close > upper_band
        
        # Atribuir sinais usando máscaras
        signals[buy_mask] = 1
        signals[sell_mask] = -1
        
        return signals

class MeanReversionEnhanced(BaseStrategy):
    def __init__(self, data: pd.DataFrame):
        super().__init__(data)
        self.risk_manager = RiskManager(data)
        self.optimize_parameters()
    
    def optimize_parameters(self):
        """Otimiza os parâmetros da estratégia usando dados históricos"""
        # Dividir dados em treino e teste
        train_size = int(len(self.data) * 0.7)
        train_data = self.data[:train_size]
        
        best_sharpe = float('-inf')
        best_params = {}
        
        # Grid search para parâmetros
        for sma_window in [10, 15, 20, 25]:
            for bb_std in [1.5, 2.0, 2.5]:
                for rsi_window in [7, 14, 21]:
                    params = {
                        'sma_window': sma_window,
                        'bb_std': bb_std,
                        'rsi_window': rsi_window
                    }
                    
                    sharpe = self._evaluate_parameters(train_data, params)
                    
                    if sharpe > best_sharpe:
                        best_sharpe = sharpe
                        best_params = params
        
        self.params = best_params
    
    def generate_signals(self) -> pd.Series:
        signals = pd.Series(0, index=self.data.index)
        
        # Usar parâmetros otimizados
        close = self.data['Close'].squeeze()
        sma = close.rolling(window=self.params['sma_window']).mean()
        std = close.rolling(window=self.params['sma_window']).std()
        
        # RSI otimizado
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.params['rsi_window']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.params['rsi_window']).mean()
        rs = gain / loss.replace(0, 1e-9)
        rsi = 100 - (100 / (1 + rs))
        
        # Bandas de Bollinger dinâmicas
        upper = sma + (self.params['bb_std'] * std)
        lower = sma - (self.params['bb_std'] * std)
        
        # Adicionar filtros de tendência
        trend = close > sma
        vol_increasing = std > std.rolling(window=20).mean()
        
        # Sinais com múltiplas confirmações
        buy_mask = (
            (close < lower) &          # Preço abaixo da banda inferior
            (rsi < 30) &              # RSI em sobrevenda
            ~trend &                   # Contra-tendência
            vol_increasing            # Volatilidade aumentando
        )
        
        sell_mask = (
            (close > upper) &          # Preço acima da banda superior
            (rsi > 70) &              # RSI em sobrecompra
            trend &                    # Com tendência
            vol_increasing            # Volatilidade aumentando
        )
        
        signals[buy_mask] = 1
        signals[sell_mask] = -1
        
        # Aplicar gestão de risco
        risk_adjusted_signals = self.risk_manager.apply_risk_management(signals)
        
        return risk_adjusted_signals

    def _evaluate_parameters(self, data: pd.DataFrame, params: Dict) -> float:
        """
        Avalia um conjunto de parâmetros usando um mini-backtest
        
        Parameters:
        -----------
        data : pd.DataFrame
            Dados para avaliação
        params : Dict
            Dicionário com os parâmetros a serem avaliados
            
        Returns:
        --------
        float
            Sharpe ratio dos retornos gerados
        """
        try:
            # Calcular indicadores com os parâmetros fornecidos
            close = data['Close'].squeeze()
            sma = close.rolling(window=params['sma_window']).mean()
            std = close.rolling(window=params['sma_window']).std()
            
            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=params['rsi_window']).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=params['rsi_window']).mean()
            rs = gain / loss.replace(0, 1e-9)
            rsi = 100 - (100 / (1 + rs))
            
            # Bandas
            upper = sma + (params['bb_std'] * std)
            lower = sma - (params['bb_std'] * std)
            
            # Gerar sinais
            signals = pd.Series(0, index=data.index)
            trend = close > sma
            vol_increasing = std > std.rolling(window=20).mean()
            
            buy_mask = (
                (close < lower) &
                (rsi < 30) &
                ~trend &
                vol_increasing
            )
            
            sell_mask = (
                (close > upper) &
                (rsi > 70) &
                trend &
                vol_increasing
            )
            
            signals[buy_mask] = 1
            signals[sell_mask] = -1
            
            # Calcular retornos
            returns = data['Close'].pct_change()
            strategy_returns = signals.shift(1) * returns
            
            # Calcular Sharpe ratio
            if len(strategy_returns) > 1 and strategy_returns.std() != 0:
                sharpe = np.sqrt(252) * strategy_returns.mean() / strategy_returns.std()
            else:
                sharpe = float('-inf')
            
            return sharpe
            
        except Exception as e:
            print(f"Erro na avaliação de parâmetros: {str(e)}")
            return float('-inf')