import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import talib

class EnhancedWDOStrategy:
    def __init__(self, data):
        self.data = data
        self.model = RandomForestClassifier(n_estimators=200, random_state=42)
        self.scaler = StandardScaler()
        
    def add_market_context(self):
        """Adiciona contexto de mercado específico para WDO"""
        df = self.data.copy()
        
        # 1. Horários importantes
        df['hour'] = df.index.hour
        df['minute'] = df.index.minute
        df['is_key_hour'] = df['hour'].isin([9, 10, 15, 16])
        
        # 2. Volume Profile
        df['poc'] = self._calculate_poc(df)
        df['vol_profile_delta'] = df['close'] - df['poc']
        
        # 3. Dados do dia anterior
        df['prev_day_close'] = df.groupby(df.index.date)['close'].shift(1)
        df['prev_day_high'] = df.groupby(df.index.date)['high'].shift(1)
        df['prev_day_low'] = df.groupby(df.index.date)['low'].shift(1)
        
        return df
    
    def add_technical_features(self, df):
        """Adiciona indicadores técnicos relevantes para WDO"""
        
        # Tendência
        df['ema9'] = talib.EMA(df['close'], timeperiod=9)
        df['ema21'] = talib.EMA(df['close'], timeperiod=21)
        df['trend_strength'] = df['ema9'] - df['ema21']
        
        # Momentum
        df['rsi'] = talib.RSI(df['close'], timeperiod=14)
        df['rsi_divergence'] = self._calculate_divergence(df['close'], df['rsi'])
        
        # Volatilidade
        df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
        df['bbands_upper'], df['bbands_middle'], df['bbands_lower'] = talib.BBANDS(
            df['close'], timeperiod=20, nbdevup=2, nbdevdn=2
        )
        
        # Volume
        df['volume_ma'] = talib.SMA(df['volume'], timeperiod=20)
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        
        return df
    
    def _calculate_poc(self, df, num_bins=100):
        """Calcula Point of Control do Volume Profile"""
        prices = np.concatenate([df['high'].values, df['low'].values])
        volumes = np.concatenate([df['volume'].values, df['volume'].values])
        
        hist, bins = np.histogram(prices, bins=num_bins, weights=volumes)
        poc_idx = np.argmax(hist)
        poc_price = (bins[poc_idx] + bins[poc_idx + 1]) / 2
        
        return poc_price
    
    def _calculate_divergence(self, price, indicator):
        """Detecta divergências entre preço e indicador"""
        price_extrema = argrelextrema(price.values, np.greater, order=5)[0]
        indicator_extrema = argrelextrema(indicator.values, np.greater, order=5)[0]
        
        divergence = np.zeros(len(price))
        
        for p_idx in price_extrema:
            for i_idx in indicator_extrema:
                if abs(p_idx - i_idx) < 5:  # Tolerância de 5 períodos
                    if price[p_idx] > price[p_idx-5] and indicator[i_idx] < indicator[i_idx-5]:
                        divergence[p_idx] = -1  # Divergência bearish
                    elif price[p_idx] < price[p_idx-5] and indicator[i_idx] > indicator[i_idx-5]:
                        divergence[p_idx] = 1  # Divergência bullish
                        
        return divergence
    
    def generate_signals(self, df):
        """Gera sinais de trading baseados em regras específicas para WDO"""
        signals = pd.Series(0, index=df.index)
        
        # Regra 1: Scalping em tendência forte
        trend_signal = np.where(
            (df['trend_strength'] > df['atr']) & 
            (df['volume_ratio'] > 1.2) &
            (df['rsi'] > 40) & (df['rsi'] < 60),
            np.sign(df['trend_strength']),
            0
        )
        
        # Regra 2: Reversão em extremos
        reversal_signal = np.where(
            (df['rsi_divergence'] != 0) &
            (df['volume_ratio'] > 1.5),
            df['rsi_divergence'],
            0
        )
        
        # Regra 3: Breakout
        breakout_signal = np.where(
            (abs(df['vol_profile_delta']) > df['atr']) &
            (df['volume_ratio'] > 2),
            np.sign(df['vol_profile_delta']),
            0
        )
        
        # Combinando sinais
        signals = pd.Series(
            trend_signal + reversal_signal + breakout_signal,
            index=df.index
        )
        
        # Filtros de horário
        signals = signals.where(
            (df['hour'].between(9, 16)) &  # Horário comercial
            (~df['hour'].isin([12, 13])),  # Evita horário de almoço
            0
        )
        
        return signals
    
    def calculate_position_size(self, df):
        """Calcula tamanho da posição baseado em volatilidade"""
        base_size = 1
        vol_factor = df['atr'] / df['atr'].rolling(20).mean()
        
        position_size = base_size * (1 / vol_factor)
        position_size = position_size.clip(0.5, 2)  # Limita entre 0.5 e 2 contratos
        
        return position_size
    
    def add_risk_management(self, df, signals):
        """Implementa regras de gestão de risco"""
        risk_adjusted_signals = signals.copy()
        
        # Stop loss dinâmico baseado em ATR
        stop_distance = df['atr'] * 1.5
        
        # Invalida sinais em condições de risco elevado
        risk_conditions = (
            (df['volume_ratio'] < 0.5) |  # Volume muito baixo
            (df['atr'] > df['atr'].rolling(20).mean() * 2)  # Volatilidade muito alta
        )
        
        risk_adjusted_signals[risk_conditions] = 0
        
        return risk_adjusted_signals, stop_distance
    
    def fit(self, start_date=None, end_date=None):
        """Treina o modelo com dados históricos"""
        df = self.data.copy()
        
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]
            
        # Prepara features
        df = self.add_market_context()
        df = self.add_technical_features(df)
        
        # Gera labels (retornos futuros simplificados)
        df['future_return'] = df['close'].shift(-1) / df['close'] - 1
        df['label'] = np.where(df['future_return'] > 0, 1, -1)
        
        # Seleciona features para o modelo
        feature_cols = [
            'trend_strength', 'rsi', 'volume_ratio', 'vol_profile_delta',
            'atr', 'is_key_hour'
        ]
        
        # Remove linhas com NA
        df = df.dropna()
        
        # Treina modelo
        X = df[feature_cols]
        y = df['label']
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        
    def predict(self, current_data):
        """Faz previsão combinando modelo e regras"""
        df = current_data.copy()
        
        # Prepara dados
        df = self.add_market_context()
        df = self.add_technical_features(df)
        
        # Gera sinais baseados em regras
        rule_signals = self.generate_signals(df)
        
        # Gera previsões do modelo
        feature_cols = [
            'trend_strength', 'rsi', 'volume_ratio', 'vol_profile_delta',
            'atr', 'is_key_hour'
        ]
        X = df[feature_cols].iloc[-1:]
        X_scaled = self.scaler.transform(X)
        model_signal = self.model.predict(X_scaled)[0]
        
        # Combina sinais
        final_signal = np.sign(rule_signals.iloc[-1] + model_signal)
        
        # Aplica gestão de risco
        risk_adjusted_signals, stop_distance = self.add_risk_management(df, pd.Series([final_signal]))
        
        position_size = self.calculate_position_size(df).iloc[-1]
        
        return {
            'signal': risk_adjusted_signals[0],
            'size': position_size,
            'stop_distance': stop_distance.iloc[-1]
        }