# main.py
from strategies import MLTradingStrategy
from backtest import Backtester
from data import MT5DataLoader
from analysis import PerformanceAnalyzer
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def main():
    # Carregar dados do banco
    print("Loading data from database...")
    db_path = r"C:\Users\rlcp0\AI Office\metatrader-data\candles.db"
    data_loader = MT5DataLoader(db_path)
    
    # Carregar dados
    data = data_loader.load_data()
    print(f"Loaded {len(data)} records")

    # Dividir dados em treino e teste
    train_size = int(len(data) * 0.7)
    train_end_date = data.index[train_size]
    
    # Criar estratégia de ML
    print("\nInitializing ML Strategy...")
    strategy = MLTradingStrategy(data)
    
    # Treinar estratégia
    print("Training strategy...")
    strategy.train(
        start_date=data.index[0].strftime('%Y-%m-%d'),
        end_date=train_end_date.strftime('%Y-%m-%d')
    )
    
    # Executar backtest
    print("\nRunning backtest...")
    backtester = Backtester(strategy)
    results = backtester.run()
    
    if not results.empty:
        # Analisar resultados
        analyzer = PerformanceAnalyzer(results, strategy.data)
        metrics = analyzer.analyze()
        
        # Imprimir resultados
        print("\nPerformance Metrics:")
        for metric, value in metrics.items():
            print(f"{metric}: {value}")
        
        # Plotar resultados
        analyzer.plot_results("ML Strategy")
    else:
        print("Backtest failed due to previous errors.")
    
    # Analisar resultados
    analyzer = PerformanceAnalyzer(results, strategy.data)
    metrics = analyzer.analyze()
    
    # Imprimir resultados
    print("\nPerformance Metrics:")
    for metric, value in metrics.items():
        print(f"{metric}: {value}")
    
    # Plotar resultados
    analyzer.plot_results("ML Strategy")

if __name__ == "__main__":
    main()