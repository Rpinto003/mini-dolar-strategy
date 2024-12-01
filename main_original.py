from strategies import MeanReversionStrategy, MeanReversionEnhanced
from backtest import Backtester
from analysis import PerformanceAnalyzer
from data import MT5DataLoader
import pandas as pd
from strategies import MLTradingStrategy
from backtest import Backtester


def main():
    # Configurar caminho do banco
    db_path = r"C:\Users\rlcp0\AI Office\metatrader-data\candles.db"
    
    # Inicializar data loader
    data_loader = MT5DataLoader(db_path)
    
    # Verificar datas disponíveis
    start_date, end_date = data_loader.get_available_dates()
    print(f"Data available from {start_date} to {end_date}")
    
    # Carregar dados
    print("\nLoading data...")
    data = data_loader.load_data()
    print(f"Loaded {len(data)} records")
    
    # Criar e treinar estratégia
    strategy = MLTradingStrategy(data)
    strategy.train('2024-01-01', '2024-10-31')

    # Testar estratégias
    strategies = {
        'Mean Reversion': MeanReversionStrategy(data),
        'Enhanced Mean Reversion': MeanReversionEnhanced(data)
    }
    
    results_summary = []
    
    for name, strategy in strategies.items():
        print(f"\nTesting {name} strategy...")
        
        # Executar backtest
        backtester = Backtester(strategy)
        results = backtester.run()
        
        # Analisar e plotar resultados
        analyzer = PerformanceAnalyzer(results, strategy.data)
        metrics = analyzer.analyze()
        
        # Imprimir métricas
        print("\nPerformance Metrics:")
        for metric, value in metrics.items():
            if metric != 'Strategy':
                print(f"{metric}: {value}")
        
        # Plotar resultados
        analyzer.plot_results(name)
    
    # Mostrar comparação
    print("\nComparative Results:")
    df_results = pd.DataFrame(results_summary)
    if not df_results.empty:
        df_results.set_index('Strategy', inplace=True)
        print(df_results)

if __name__ == "__main__":
    main()