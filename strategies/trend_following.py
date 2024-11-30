from .base_strategy import BaseStrategy
import pandas as pd

class TrendFollowingStrategy(BaseStrategy):
    def __init__(self, data: pd.DataFrame, risk_manager, fast_ma: int = 20, slow_ma: int = 50):
        super().__init__(data, risk_manager)
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma
    
    def generate_signals(self) -> pd.Series:
        fast = self.data['close'].rolling(window=self.fast_ma).mean()
        slow = self.data['close'].rolling(window=self.slow_ma).mean()
        signals = pd.Series(index=self.data.index, data=0)
        signals[fast > slow] = 1
        signals[fast < slow] = -1
        return signals