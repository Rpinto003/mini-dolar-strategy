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
        self.prepared_data = None

    def prepare_all_data(self):
        """Prepara todos os dados uma única vez"""
        print("\nPreparando todos os dados...")
        df = self.data.copy()
        
        # 1. Adiciona informações de horário
        print("Adicionando informações de horário...")
        df['hour'] = df.index.hour
        df['minute'] = df.index.minute
        df['is_key_hour'] = df['hour'].isin([9, 10, 15, 16])
        
        # 2. Calcula POC por dia
        print("Calculando POC diário...")
        df['date'] = df.index.date
        
        # Calcula POC por dia
        poc_values = []
        unique_dates = df['date'].unique()
        for date in unique_dates:
            daily_data = df[df['date'] == date]
            poc = self._calculate_poc_daily(daily_data)
            poc_values.extend([poc] * len(daily_data))
        
        df['poc'] = poc_values
        df['vol_profile_delta'] = df['close'] - df['poc']
        
        # Remove coluna auxiliar
        df = df.drop('date', axis=1)
        
        # 3. Dados do dia anterior
        print("Processando dados do dia anterior...")
        df['prev_day_close'] = df.groupby(df.index.date)['close'].shift(1)
        df['prev_day_high'] = df.groupby(df.index.date)['high'].shift(1)
        df['prev_day_low'] = df.groupby(df.index.date)['low'].shift(1)
        
        # 4. Adiciona indicadores técnicos
        print("Calculando indicadores técnicos...")
        df = self.add_technical_features(df)
        
        # Verifica dados antes de armazenar
        print("\nShape final dos dados preparados:", df.shape)
        print("\nVerificando NaN nos dados preparados:")
        for col in df.columns:
            nan_count = df[col].isna().sum()
            if nan_count > 0:
                print(f"{col}: {nan_count} NaN values")
        
        self.prepared_data = df
        return df

    def add_market_context(self):
        """Adiciona contexto de mercado específico para WDO"""
        df = self.data.copy()
        
        print("\nAdicionando contexto de mercado...")
        print(f"Shape dos dados: {df.shape}")
        print(f"Colunas disponíveis: {df.columns.tolist()}")
        
        # 1. Horários importantes
        df['hour'] = df.index.hour
        df['minute'] = df.index.minute
        df['is_key_hour'] = df['hour'].isin([9, 10, 15, 16])
        
        # 2. Volume Profile
        print("Calculando POC...")
        df['poc'] = self._calculate_poc_daily(df)
        df['vol_profile_delta'] = df['close'] - df['poc']
        
        # 3. Dados do dia anterior
        df['prev_day_close'] = df.groupby(df.index.date)['close'].shift(1)
        df['prev_day_high'] = df.groupby(df.index.date)['high'].shift(1)
        df['prev_day_low'] = df.groupby(df.index.date)['low'].shift(1)
        
        return df
    
    def add_technical_features(self, df):
        """Adiciona indicadores técnicos relevantes para WDO"""
        print("\nAdicionando indicadores técnicos...")
        
        # Tendência
        print("Calculando EMAs...")
        df['ema9'] = talib.EMA(df['close'], timeperiod=9)
        df['ema21'] = talib.EMA(df['close'], timeperiod=21)
        df['trend_strength'] = df['ema9'] - df['ema21']
        
        # Momentum
        print("Calculando RSI...")
        df['rsi'] = talib.RSI(df['close'], timeperiod=14)
        df['rsi_divergence'] = self._calculate_divergence(df['close'], df['rsi'])
        
        # Volatilidade
        print("Calculando ATR e Bandas de Bollinger...")
        df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
        df['bbands_upper'], df['bbands_middle'], df['bbands_lower'] = talib.BBANDS(
            df['close'], timeperiod=20, nbdevup=2, nbdevdn=2
        )
        
        # Volume
        print("Calculando indicadores de volume...")
        df['volume_ma'] = talib.SMA(df['volume'], timeperiod=20)
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        
        # Verifica quais colunas têm NaN
        print("\nVerificando NaN após adicionar indicadores:")
        for col in df.columns:
            nan_count = df[col].isna().sum()
            if nan_count > 0:
                print(f"{col}: {nan_count} NaN values")
        
        return df
    
    def _calculate_poc_daily(self, daily_data):
        """Calcula POC para um único dia"""
        try:
            prices = np.concatenate([daily_data['high'].values, daily_data['low'].values])
            volumes = np.concatenate([daily_data['volume'].values, daily_data['volume'].values])
            
            if len(prices) > 0 and len(volumes) > 0:
                hist, bins = np.histogram(prices, bins=100, weights=volumes)
                poc_idx = np.argmax(hist)
                return (bins[poc_idx] + bins[poc_idx + 1]) / 2
            else:
                return daily_data['close'].mean()  # Fallback para média do dia
        except Exception as e:
            print(f"Erro no cálculo do POC: {e}")
            return daily_data['close'].mean()  # Fallback para média do dia
    
    def _calculate_divergence(self, price, indicator):
        """Detecta divergências entre preço e indicador"""
        price_extrema = argrelextrema(price.values, np.greater, order=5)[0]
        indicator_extrema = argrelextrema(indicator.values, np.greater, order=5)[0]
        
        divergence = np.zeros(len(price))
        
        for p_idx in price_extrema:
            for i_idx in indicator_extrema:
                if abs(p_idx - i_idx) < 5:  # Tolerância de 5 períodos
                    if price.iloc[p_idx] > price.iloc[p_idx-5] and indicator.iloc[i_idx] < indicator.iloc[i_idx-5]:
                        divergence[p_idx] = -1  # Divergência bearish
                    elif price.iloc[p_idx] < price.iloc[p_idx-5] and indicator.iloc[i_idx] > indicator.iloc[i_idx-5]:
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
        # Stop loss dinâmico baseado em ATR
        stop_distance = df['atr'] * 1.5
        
        # Invalida sinais em condições de risco elevado
        risk_conditions = (
            (df['volume_ratio'] < 0.5) |  # Volume muito baixo
            (df['atr'] > df['atr'].rolling(20).mean() * 2)  # Volatilidade muito alta
        )
        
        # Pega apenas o último valor das condições de risco
        last_risk_condition = risk_conditions.iloc[-1]
        
        # Se houver condição de risco, zera o sinal
        if last_risk_condition:
            risk_adjusted_signals = pd.Series([0], index=signals.index)
        else:
            risk_adjusted_signals = signals.copy()
        
        return risk_adjusted_signals, stop_distance.iloc[-1]
    
    def fit(self, start_date=None, end_date=None):
        """Treina o modelo com dados históricos"""
        print("\nIniciando treinamento...")
        
        # Prepara todos os dados uma única vez se ainda não preparou
        if self.prepared_data is None:
            self.prepare_all_data()
        
        df = self.prepared_data.copy()
        
        # Filtra período de treinamento
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]
        
        # Gera labels
        print("Gerando labels...")
        df['future_return'] = df['close'].shift(-1) / df['close'] - 1
        df['label'] = np.where(df['future_return'] > 0, 1, -1)
        
        # Seleciona features
        feature_cols = [
            'trend_strength', 'rsi', 'volume_ratio', 'vol_profile_delta',
            'atr', 'is_key_hour'
        ]
        
        # Remove apenas as primeiras linhas com NaN (devido ao período de cálculo dos indicadores)
        first_valid_idx = df[feature_cols].notna().all(axis=1).idxmax()
        df = df.loc[first_valid_idx:]
        
        print(f"\nShape após remover período inicial: {df.shape}")
        
        if df.empty:
            raise ValueError("DataFrame está vazio após processar dados!")
        
        # Treina modelo
        print("\nTreinando modelo...")
        X = df[feature_cols]
        y = df['label']
        
        print(f"Shape dos dados de treino (X): {X.shape}")
        print(f"Shape dos labels (y): {y.shape}")
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        print("Treinamento concluído!")
        
    def predict(self, current_data):
        """Faz previsão usando dados pré-processados"""
        try:
            # Usa os dados já preparados até o índice atual
            last_idx = current_data.index[-1]
            df = self.prepared_data.loc[:last_idx].copy()
            
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
            
            # Calcula tamanho da posição
            position_size = self.calculate_position_size(df).iloc[-1]
            
            return {
                'date': last_idx,
                'price': df['close'].iloc[-1],
                'signal': final_signal,
                'size': position_size,
                'stop_distance': df['atr'].iloc[-1] * 1.5
            }
        except Exception as e:
            print(f"Erro na previsão: {e}")
            return None