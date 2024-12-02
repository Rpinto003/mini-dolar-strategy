import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Callable
from sklearn.metrics import mean_squared_error, mean_absolute_error
from src.evaluation.backtesting import BacktestEngine
import logging

class TimeSeriesValidator:
    def __init__(self, n_splits: int = 5, test_size: int = 63):
        """Inicializa validador de séries temporais.
        
        Args:
            n_splits: Número de splits para validação
            test_size: Tamanho da janela de teste em dias
        """
        self.n_splits = n_splits
        self.test_size = test_size
        self.results = []
        
        # Configura logging
        self.logger = logging.getLogger(__name__)
        
    def generate_validation_splits(self, data: pd.DataFrame) -> List[Dict]:
        """Gera splits para validação cruzada em séries temporais.
        
        Args:
            data: DataFrame com dados
            
        Returns:
            List[Dict]: Lista de dicionários com índices de treino e teste
        """
        splits = []
        total_size = len(data)
        
        for i in range(self.n_splits):
            test_end = total_size - (i * self.test_size)
            test_start = test_end - self.test_size
            
            if test_start < self.test_size:
                break
                
            split = {
                'train': {
                    'start': 0,
                    'end': test_start
                },
                'test': {
                    'start': test_start,
                    'end': test_end
                }
            }
            splits.append(split)
            
        self.logger.info(f"Gerados {len(splits)} splits para validação")
        return splits
    
    def calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray,
                         returns: pd.Series) -> Dict:
        """Calcula métricas de avaliação.
        
        Args:
            y_true: Valores reais
            y_pred: Valores previstos
            returns: Série de retornos
            
        Returns:
            Dict: Métricas calculadas
        """
        # Métricas de erro
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        
        # Métricas de retorno
        total_return = (1 + returns).prod() - 1
        annual_return = (1 + total_return) ** (252 / len(returns)) - 1
        
        # Volatilidade
        volatility = returns.std() * np.sqrt(252)
        
        # Sharpe e Sortino
        risk_free_rate = 0.0525  # Taxa SELIC atual como referência
        excess_returns = returns - risk_free_rate/252
        sharpe_ratio = np.sqrt(252) * (excess_returns.mean() / returns.std())
        
        negative_returns = returns[returns < 0]
        sortino_ratio = np.sqrt(252) * (excess_returns.mean() / negative_returns.std())
        
        # Máximo Drawdown
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdowns.min()
        
        metrics = {
            'rmse': rmse,
            'mae': mae,
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown
        }
        
        self.logger.info(f"Métricas calculadas: {metrics}")
        return metrics
    
    def validate_model(self, model: object, data: pd.DataFrame,
                       feature_columns: List[str],
                       target_column: str) -> pd.DataFrame:
        """Executa validação cruzada do modelo.
        
        Args:
            model: Modelo a ser validado
            data: DataFrame com dados
            feature_columns: Lista de colunas de features
            target_column: Coluna alvo
            
        Returns:
            DataFrame com resultados da validação
        """
        splits = self.generate_validation_splits(data)
        results = []
        
        for i, split in enumerate(splits):
            self.logger.info(f"Processando split {i+1}/{len(splits)}")
            
            # Separa dados de treino e teste
            train_data = data.iloc[split['train']['start']:split['train']['end']]
            test_data = data.iloc[split['test']['start']:split['test']['end']]
            
            # Treina modelo
            X_train = train_data[feature_columns]
            y_train = train_data[target_column]
            model.fit(X_train, y_train)
            
            # Faz predições
            X_test = test_data[feature_columns]
            y_test = test_data[target_column]
            y_pred = model.predict(X_test)
            
            # Calcula retornos
            test_returns = test_data['Close'].pct_change().dropna()
            
            # Calcula métricas
            metrics = self.calculate_metrics(y_test, y_pred, test_returns)
            metrics['split'] = i
            results.append(metrics)
        
        results_df = pd.DataFrame(results)
        self.results = results_df
        
        # Calcula médias e desvios
        summary = results_df.agg(['mean', 'std'])
        self.logger.info(f"\nResumo da validação:\n{summary}")
        
        return results_df
    
    def plot_validation_results(self):
        """Plota resultados da validação."""
        if self.results.empty:
            raise ValueError("Execute validate_model primeiro")
            
        import matplotlib.pyplot as plt
        
        metrics = ['sharpe_ratio', 'sortino_ratio', 'total_return', 'max_drawdown']
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Resultados da Validação Cruzada')
        
        for i, metric in enumerate(metrics):
            ax = axes[i//2, i%2]
            self.results[metric].plot(kind='bar', ax=ax)
            ax.set_title(metric)
            ax.grid(True)
        
        plt.tight_layout()
        plt.show()
        
    def generate_validation_report(self, output_path: str = 'validation_report.html'):
        """Gera relatório detalhado da validação.
        
        Args:
            output_path: Caminho para salvar o relatório HTML
        """
        if self.results.empty:
            raise ValueError("Execute validate_model primeiro")
            
        import pandas as pd
        
        # Cria HTML
        html = "<h1>Relatório de Validação do Modelo</h1>\n"
        
        # Estatísticas gerais
        html += "<h2>Estatísticas Gerais</h2>\n"
        stats = self.results.describe()
        html += stats.to_html()
        
        # Resultados por split
        html += "<h2>Resultados por Split</h2>\n"
        html += self.results.to_html()
        
        # Salva relatório
        with open(output_path, 'w') as f:
            f.write(html)
            
        self.logger.info(f"Relatório salvo em {output_path}")