import lightgbm as lgb
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.utils import class_weight
import numpy as np
import pandas as pd
from typing import Dict, Tuple

class MLModel:
    """Classe responsável pelo treinamento e predição"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()

    def train(self, X: pd.DataFrame, y: pd.Series):
        """Treina o modelo"""
        print("Scaling features...")
        X_scaled = self.scaler.fit_transform(X)
        
        # Definir os parâmetros do LightGBM
        params = {
            'objective': 'multiclass',
            'num_class': 3,
            'learning_rate': 0.1,
            'max_depth': 8,
            'num_leaves': 128,
            'min_child_samples': 10,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.9,
            'metric': 'multi_logloss'  # Definir explicitamente o métrico
        }
        
        print("Calculando pesos de classe...")
        # Calcular pesos de classe
        class_weights = class_weight.compute_class_weight(
            class_weight='balanced',
            classes=np.unique(y),
            y=y
        )
        class_weight_dict = dict(zip(np.unique(y), class_weights))
        sample_weights = y.map(class_weight_dict)

        print("Setting up cross-validation...")
        tscv = TimeSeriesSplit(n_splits=5)
        models = []
        
        for fold, (train_idx, val_idx) in enumerate(tscv.split(X_scaled), 1):
            print(f"\nTraining fold {fold}/5...")
            X_train, X_val = X_scaled[train_idx], X_scaled[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            sample_weights_train = sample_weights.iloc[train_idx]
            sample_weights_val = sample_weights.iloc[val_idx]
            
            # Criar datasets do LightGBM com pesos de amostra
            train_dataset = lgb.Dataset(X_train, label=y_train, weight=sample_weights_train)
            val_dataset = lgb.Dataset(X_val, label=y_val, weight=sample_weights_val, reference=train_dataset)
            
            # Treinar modelo
            model = lgb.train(
                params=params,
                train_set=train_dataset,
                valid_sets=[train_dataset, val_dataset],
                num_boost_round=1000,
                callbacks=[
                    lgb.early_stopping(stopping_rounds=50),
                    lgb.log_evaluation(period=100)
                ]
            )
            
            models.append(model)
            print(f"Fold {fold} completed.")

        print("\nClass distribution in training data:")
        print(y_train.value_counts().sort_index())
        print("\nTraining model...")

        self.model = models
        print("\nTraining completed successfully.")
    
    def predict(self, X: pd.DataFrame) -> pd.Series:
        """Faz predições utilizando o modelo treinado"""
        if self.model is None:
            raise ValueError("Model needs to be trained first")
                
        X_scaled = self.scaler.transform(X)
        predictions = np.zeros((len(X), 3))
        
        for model in self.model:
            pred = model.predict(X_scaled)
            predictions += pred
        predictions /= len(self.model)
        
        # Gerar sinais com base na classe com maior probabilidade
        predicted_classes = np.argmax(predictions, axis=1)
        signals = pd.Series(predicted_classes - 1, index=X.index)  # Ajustar para -1, 0, 1
        
        # Debug info
        print("\nPrevisão Summary:")
        print(f"Total samples: {len(signals)}")
        print(f"CALL signals: {sum(signals == 1)}")
        print(f"PUT signals: {sum(signals == -1)}")
        print(f"No signals: {sum(signals == 0)}")
        
        # Distribuição de probabilidades
        print("\nProbability Distribution:")
        print(f"Mean CALL prob: {predictions[:, 2].mean():.3f}")
        print(f"Mean PUT prob: {predictions[:, 0].mean():.3f}")
        print(f"Mean neutral prob: {predictions[:, 1].mean():.3f}")
        
        return signals
    
    def create_technical_features(self) -> pd.DataFrame:
        df = pd.DataFrame(index=self.data.index)
        
        close = self.data['Close']
        
        # Features básicas
        df['returns'] = close.pct_change()
        df['log_returns'] = np.log(close).diff()
        
        # Médias móveis em diferentes períodos
        for window in [5, 10, 20, 50]:
            df[f'sma_{window}'] = close.rolling(window=window).mean()
            df[f'sma_dist_{window}'] = (close - df[f'sma_{window}']) / df[f'sma_{window}']
        
        # Volatilidade
        for window in [5, 15, 30]:
            df[f'volatility_{window}'] = df['returns'].rolling(window=window).std()
        
        # Momentum
        df['momentum_1d'] = close.pct_change(1)
        df['momentum_5d'] = close.pct_change(5)
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, 1e-9)
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df

    def create_wdo_features(self) -> pd.DataFrame:
        df = pd.DataFrame(index=self.data.index)
        
        # Padrões intraday
        df['hour'] = self.data.index.hour
        df['minute'] = self.data.index.minute
        
        # Volume patterns
        df['volume_ma'] = self.data['Volume'].rolling(20).mean()
        df['volume_ratio'] = self.data['Volume'] / df['volume_ma']
        
        # Price patterns
        df['range'] = self.data['High'] - self.data['Low']
        df['range_ma'] = df['range'].rolling(20).mean()
        
        # Momentum em diferentes timeframes
        for window in [5, 15, 30, 60]:
            df[f'return_{window}'] = self.data['Close'].pct_change(window)
                
        return df