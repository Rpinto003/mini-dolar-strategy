import pandas as pd
import numpy as np

class TechnicalIndicators:
    @staticmethod
    def sma(data: pd.Series, window: int) -> pd.Series:
        """Simple Moving Average"""
        return data.rolling(window=window).mean()
    
    @staticmethod
    def ema(data: pd.Series, window: int) -> pd.Series:
        """Exponential Moving Average"""
        return data.ewm(span=window, adjust=False).mean()
    
    @staticmethod
    def bollinger_bands(data: pd.Series, window: int = 20, num_std: float = 2.0) -> tuple:
        """Calculate Bollinger Bands"""
        middle_band = TechnicalIndicators.sma(data, window)
        std = data.rolling(window=window).std()
        upper_band = middle_band + (std * num_std)
        lower_band = middle_band - (std * num_std)
        return upper_band, middle_band, lower_band
    
    @staticmethod
    def rsi(data: pd.Series, window: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def macd(data: pd.Series, fast_window: int = 12, slow_window: int = 26, signal_window: int = 9) -> tuple:
        """Moving Average Convergence Divergence"""
        fast_ema = TechnicalIndicators.ema(data, fast_window)
        slow_ema = TechnicalIndicators.ema(data, slow_window)
        macd_line = fast_ema - slow_ema
        signal_line = TechnicalIndicators.ema(macd_line, signal_window)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
        """Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=window).mean()
    
    @staticmethod
    def adx(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> tuple:
        """Average Directional Index"""
        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        
        tr = TechnicalIndicators.atr(high, low, close, window)
        plus_di = 100 * (plus_dm.rolling(window).mean() / tr)
        minus_di = 100 * (minus_dm.rolling(window).mean() / tr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window).mean()
        
        return adx, plus_di, minus_di