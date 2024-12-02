import pandas as pd
import numpy as np
from typing import Dict, List, Callable
from sklearn.model_selection import ParameterGrid
from concurrent.futures import ProcessPoolExecutor, as_completed
from src.evaluation.backtesting import BacktestEngine

class StrategyOptimizer:
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.results = []
        
    def evaluate_parameters(self, data: pd.DataFrame, 
                           strategy_class: object,
                           parameters: Dict,
                           metric: str = 'sharpe_ratio') -> Dict:
        """Avalia um conjunto de parâmetros.
        
        Args:
            data: DataFrame com dados de mercado
            strategy_class: Classe da estratégia
            parameters: Dicionário com parâmetros
            metric: Métrica para otimização
            
        Returns:
            Dict: Resultados da avaliação
        """
        try:
            # Instancia estratégia com parâmetros
            strategy = strategy_class(**parameters)
            
            # Gera sinais
            signals = strategy.generate_signals(data)
            
            # Executa backtest
            backtest = BacktestEngine(initial_capital=self.initial_capital)
            results = backtest.run_backtest(data, signals)
            stats = backtest.get_statistics()
            
            # Calcula Sharpe Ratio
            returns = results['capital'].pct_change().dropna()
            sharpe_ratio = np.sqrt(252) * (returns.mean() / returns.std())
            
            # Calcula Sortino Ratio
            negative_returns = returns[returns < 0]
            sortino_ratio = np.sqrt(252) * (returns.mean() / negative_returns.std())
            
            evaluation = {
                'parameters': parameters,
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': sortino_ratio,
                'total_return': stats['return'],
                'max_drawdown': stats['max_drawdown'],
                'win_rate': stats['win_rate']
            }
            
            return evaluation
            
        except Exception as e:
            print(f"Erro ao avaliar parâmetros {parameters}: {str(e)}")
            return None
    
    def optimize(self, data: pd.DataFrame,
                 strategy_class: object,
                 parameter_grid: Dict[str, List],
                 metric: str = 'sharpe_ratio',
                 n_jobs: int = -1) -> pd.DataFrame:
        """Otimiza parâmetros da estratégia.
        
        Args:
            data: DataFrame com dados de mercado
            strategy_class: Classe da estratégia
            parameter_grid: Grade de parâmetros para otimização
            metric: Métrica para otimização
            n_jobs: Número de processos paralelos
            
        Returns:
            DataFrame com resultados da otimização
        """
        # Gera todas as combinações de parâmetros
        param_combinations = list(ParameterGrid(parameter_grid))
        results = []
        
        # Executa otimização em paralelo
        with ProcessPoolExecutor(max_workers=n_jobs) as executor:
            futures = []
            for params in param_combinations:
                future = executor.submit(
                    self.evaluate_parameters,
                    data,
                    strategy_class,
                    params,
                    metric
                )
                futures.append(future)
            
            # Coleta resultados
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    results.append(result)
        
        # Organiza resultados
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values(metric, ascending=False)
        
        self.results = results_df
        return results_df
    
    def get_best_parameters(self, metric: str = 'sharpe_ratio') -> Dict:
        """Retorna os melhores parâmetros encontrados.
        
        Args:
            metric: Métrica para otimização
            
        Returns:
            Dict: Melhores parâmetros
        """
        if self.results.empty:
            raise ValueError("Execute optimize() primeiro")
            
        return self.results.iloc[0]['parameters']
    
    def plot_optimization_results(self, param_name: str,
                                metric: str = 'sharpe_ratio'):
        """Plota resultados da otimização para um parâmetro.
        
        Args:
            param_name: Nome do parâmetro para plotar
            metric: Métrica para plotar
        """
        import matplotlib.pyplot as plt
        
        if self.results.empty:
            raise ValueError("Execute optimize() primeiro")
        
        # Extrai valores do parâmetro
        param_values = [result[param_name] 
                       for result in self.results['parameters']]
        
        plt.figure(figsize=(10, 6))
        plt.scatter(param_values, self.results[metric])
        plt.xlabel(param_name)
        plt.ylabel(metric)
        plt.title(f'Resultados da Otimização - {param_name} vs {metric}')
        plt.grid(True)
        plt.show()

class WalkForwardOptimizer:
    def __init__(self, train_size: int = 252, test_size: int = 63):
        """Inicializa otimizador walk-forward.
        
        Args:
            train_size: Tamanho da janela de treino em dias
            test_size: Tamanho da janela de teste em dias
        """
        self.train_size = train_size
        self.test_size = test_size
        self.results = []
        
    def generate_windows(self, data: pd.DataFrame) -> List[Dict]:
        """Gera janelas de treino e teste.
        
        Args:
            data: DataFrame com dados de mercado
            
        Returns:
            List[Dict]: Lista de dicionários com índices de treino e teste
        """
        windows = []
        start = 0
        
        while (start + self.train_size + self.test_size) <= len(data):
            window = {
                'train': {
                    'start': start,
                    'end': start + self.train_size
                },
                'test': {
                    'start': start + self.train_size,
                    'end': start + self.train_size + self.test_size
                }
            }
            windows.append(window)
            start += self.test_size
            
        return windows
    
    def optimize(self, data: pd.DataFrame,
                 strategy_class: object,
                 parameter_grid: Dict[str, List],
                 metric: str = 'sharpe_ratio',
                 n_jobs: int = -1) -> pd.DataFrame:
        """Executa otimização walk-forward.
        
        Args:
            data: DataFrame com dados de mercado
            strategy_class: Classe da estratégia
            parameter_grid: Grade de parâmetros para otimização
            metric: Métrica para otimização
            n_jobs: Número de processos paralelos
            
        Returns:
            DataFrame com resultados da otimização
        """
        windows = self.generate_windows(data)
        results = []
        
        for window in windows:
            # Separa dados de treino e teste
            train_data = data.iloc[window['train']['start']:window['train']['end']]
            test_data = data.iloc[window['test']['start']:window['test']['end']]
            
            # Otimiza parâmetros no conjunto de treino
            optimizer = StrategyOptimizer()
            train_results = optimizer.optimize(
                train_data,
                strategy_class,
                parameter_grid,
                metric,
                n_jobs
            )
            
            # Obtém melhores parâmetros
            best_params = optimizer.get_best_parameters(metric)
            
            # Avalia no conjunto de teste
            test_evaluation = optimizer.evaluate_parameters(
                test_data,
                strategy_class,
                best_params,
                metric
            )
            
            results.append({
                'window': window,
                'train_results': train_results,
                'test_results': test_evaluation,
                'best_parameters': best_params
            })
        
        self.results = results
        return pd.DataFrame(results)
    
    def plot_walk_forward_results(self, metric: str = 'sharpe_ratio'):
        """Plota resultados da otimização walk-forward.
        
        Args:
            metric: Métrica para plotar
        """
        import matplotlib.pyplot as plt
        
        if not self.results:
            raise ValueError("Execute optimize() primeiro")
        
        train_metrics = [result['train_results'][metric].max() 
                        for result in self.results]
        test_metrics = [result['test_results'][metric] 
                       for result in self.results]
        
        plt.figure(figsize=(12, 6))
        plt.plot(train_metrics, label='Treino', marker='o')
        plt.plot(test_metrics, label='Teste', marker='s')
        plt.xlabel('Janela')
        plt.ylabel(metric)
        plt.title(f'Resultados Walk-Forward - {metric}')
        plt.legend()
        plt.grid(True)
        plt.show()