# main.py
from enhanced_strategy import EnhancedWDOStrategy
from backtest import Backtester
from data import MT5DataLoader
from analysis import PerformanceAnalyzer
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def prepare_data(data):
    """Padroniza os nomes das colunas do DataFrame"""
    print("\nColunas originais do DataFrame:")
    print(data.columns.tolist())
    
    # Converter todos os nomes de colunas para minúsculo
    data.columns = data.columns.str.lower()
    
    # Usar realvolume como volume principal e remover a coluna volume original
    if 'realvolume' in data.columns:
        data['volume'] = data['realvolume']
        data = data.drop(['realvolume'], axis=1)
    
    # Verificar colunas necessárias
    required_columns = ['high', 'low', 'close', 'volume']
    missing_columns = [col for col in required_columns if col not in data.columns]
    
    if missing_columns:
        raise ValueError(f"Colunas ausentes no DataFrame: {missing_columns}")
    
    print("\nColunas após padronização:")
    print(data.columns.tolist())
    
    return data

def main():
    # Carregar dados do banco
    print("Loading data from database...")
    db_path = r"C:\Users\rlcp0\AI Office\metatrader-data\candles.db"
    data_loader = MT5DataLoader(db_path)
    
    # Carregar dados
    data = data_loader.load_data()
    print(f"Loaded {len(data)} records")
    
    # Preparar dados
    try:
        data = prepare_data(data)
        print("\nDados preparados com sucesso!")
    except ValueError as e:
        print(f"\nErro na preparação dos dados: {e}")
        return
    
    # Dividir dados em treino e teste
    train_size = int(len(data) * 0.7)
    train_end_date = data.index[train_size]
    
    # Criar estratégia melhorada
    print("\nInitializing Enhanced WDO Strategy...")
    strategy = EnhancedWDOStrategy(data)
    
    # Treinar estratégia
    print("Training strategy...")
    strategy.fit(
        start_date=data.index[0].strftime('%Y-%m-%d'),
        end_date=train_end_date.strftime('%Y-%m-%d')
    )
    
    # Executar backtest com a nova estratégia
    print("\nRunning backtest...")
    results = []
    total_steps = len(data) - train_size
    
    for i in range(train_size, len(data)):
        if i % 100 == 0:
            progress = ((i - train_size) / total_steps) * 100
            print(f"Progresso do backtest: {progress:.1f}%")
            
        current_data = data.iloc[:i+1]
        prediction = strategy.predict(current_data)
        
        results.append({
            'date': prediction['date'],
            'price': prediction['price'],
            'signal': prediction['signal'],
            'size': prediction['size'],
            'stop_distance': prediction['stop_distance']
        })
    
    # Converter resultados para DataFrame com índice correto
    results_df = pd.DataFrame(results)
    results_df.set_index('date', inplace=True)
    
    if not results_df.empty:
        # Analisar resultados
        analyzer = PerformanceAnalyzer(results_df, data)
        metrics = analyzer.analyze()
        
        # Imprimir resultados
        print("\nPerformance Metrics:")
        for metric, value in metrics.items():
            print(f"{metric}: {value}")
        
        # Plotar resultados
        analyzer.plot_results("Enhanced WDO Strategy")
    else:
        print("Backtest failed: no results generated")

if __name__ == "__main__":
    main()