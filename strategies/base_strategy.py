from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    def __init__(self, data: pd.DataFrame, risk_manager):
        self.data = data
        self.risk_manager = risk_manager

    @abstractmethod
    def generate_signals(self) -> pd.Series:
        pass