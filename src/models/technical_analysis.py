import pandas as pd
import numpy as np
from typing import List, Dict

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators for the dataset.
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data
        
    Returns:
        pd.DataFrame: DataFrame with technical indicators
    """
    df = df.copy()
    
    # Moving averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # Relative Strength Index (RSI)
    def calculate_rsi(data: pd.Series, periods: int = 14) -> pd.Series:
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    df['RSI'] = calculate_rsi(df['Close'])
    
    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    return df

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Generate trading signals based on technical indicators.
    
    Args:
        df (pd.DataFrame): DataFrame with technical indicators
        
    Returns:
        pd.DataFrame: DataFrame with trading signals
    """
    df = df.copy()
    
    # Example signal generation
    df['Signal'] = 0
    df.loc[(df['MACD'] > df['Signal_Line']) & (df['RSI'] < 70), 'Signal'] = 1  # Buy
    df.loc[(df['MACD'] < df['Signal_Line']) & (df['RSI'] > 30), 'Signal'] = -1  # Sell
    
    return df

def main():
    # Example usage
    from collect_market_data import fetch_wdo_data
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    df = fetch_wdo_data(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    
    df = calculate_technical_indicators(df)
    df = generate_signals(df)
    print(df.tail())

if __name__ == '__main__':
    main()
