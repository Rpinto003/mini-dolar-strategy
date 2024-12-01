# strategies/base_strategy.py
from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    def __init__(self, data: pd.DataFrame):
        self.data = data
    
    @abstractmethod
    def generate_signals(self) -> pd.Series:
        pass