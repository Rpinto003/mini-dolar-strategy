from strategies import MeanReversionStrategy, TrendFollowingStrategy
from backtest import Backtester
from analysis import PerformanceAnalyzer
import yfinance as yf

def main():
    # Download data
    data = yf.download('USDBRL=X', start='2020-01-01')
    
    # Create strategies
    mean_rev = MeanReversionStrategy(data, risk_manager)
    trend = TrendFollowingStrategy(data, risk_manager)
    
    # Run backtest
    backtester = Backtester(mean_rev)
    results = backtester.run()
    
    # Analyze results
    analyzer = PerformanceAnalyzer(results)
    metrics = analyzer.calculate_metrics()
    print(metrics)

if __name__ == '__main__':
    main()