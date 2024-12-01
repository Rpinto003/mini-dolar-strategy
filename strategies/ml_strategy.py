from .base_strategy import BaseStrategy
from ml_strategy.data_processor import DataProcessor
from ml_strategy.model import MLModel
from strategies.risk_manager import RiskManager
import pandas as pd

class MLTradingStrategy(BaseStrategy):
    """Estratégia de trading baseada em machine learning"""
    
    def __init__(self, data: pd.DataFrame):
        super().__init__(data)
        self.data_processor = DataProcessor(data)
        self.model = MLModel()
        self.trained = False
        self.trade_params = {}
        self.risk_manager = RiskManager(data)
        
    def _create_labels(self, horizon: int = 5) -> pd.Series:
        """
        Criar labels para treinamento do modelo
        
        Parameters:
        -----------
        horizon : int
            Horizonte de previsão em períodos
                
        Returns:
        --------
        pd.Series
            Labels para treinamento (0 para PUT, 1 para neutro, 2 para CALL)
        """
        # Calcular retornos futuros
        future_returns = self.data['Close'].pct_change(horizon).shift(-horizon)
        
        # Definir thresholds para opções
        call_threshold = 0.0003  # 0.03% para CALL
        put_threshold = -0.0003  # -0.03% para PUT
        
        # Criar labels (começando de 0 para LightGBM)
        labels = pd.Series(1, index=self.data.index)  # 1 é neutro
        
        # 2 para CALL (Alta esperada)
        labels[future_returns > call_threshold] = 2
        
        # 0 para PUT (Baixa esperada)
        labels[future_returns < put_threshold] = 0
        
        return labels.fillna(1)  # Preencher NaN com 1 (neutro)
    
    def train(self, start_date: str, end_date: str):
        """Treina a estratégia"""
        print("Preparing features...")
        X = self.data_processor.prepare_features()
        
        print("Creating labels...")
        y = self._create_labels()
        
        # Garantir que X e y têm os mesmos índices
        common_index = X.index.intersection(y.index)
        X = X.loc[common_index]
        y = y.loc[common_index]
        
        # Alinhar dados de treino com as datas
        mask = (X.index >= start_date) & (X.index <= end_date)
        X_train = X[mask]
        y_train = y[mask]
        
        print(f"Training model with {len(X_train)} samples...")
        
        # Verificar se temos dados suficientes
        if len(X_train) < 100:  # número mínimo arbitrário de amostras
            raise ValueError("Insufficient training data")
            
        self.model.train(X_train, y_train)
        self.trained = True
        print("Model training completed.")
        
        # Imprimir estatísticas do treinamento
        print("\nTraining Statistics:")
        print(f"Total samples: {len(X_train)}")
        print(f"Class distribution:")
        print(y_train.value_counts().to_dict())
    
    def generate_signals(self) -> pd.Series:
        """Gera sinais de trading"""
        if not self.trained:
            raise ValueError("Strategy needs to be trained first")
            
        features = self.data_processor.prepare_features()
        predictions = self.model.predict(features)
        
        signals = pd.Series(0, index=self.data.index)
        current_price = self.data['Close'].iloc[-1]
        
        for i in range(len(predictions)):
            if predictions[i] != 0:
                # Validar trade
                is_valid, reason = self.risk_manager.validate_trade(
                    predictions[i],
                    current_price,
                    features['volatility_60'].iloc[i]
                )
                
                if is_valid:
                    # Calcular parâmetros da opção
                    option_params = self.risk_manager.calculate_option_parameters(
                        predictions[i],
                        current_price
                    )
                    
                    # Armazenar sinal e parâmetros
                    signals.iloc[i] = predictions[i]
                    self.trade_params[signals.index[i]] = option_params
        
        return signals