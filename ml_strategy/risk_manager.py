import pandas as pd
import numpy as np
from typing import Dict, Tuple

class RiskManager:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.position_size = 1.0
        self.max_trades_per_day = 5
        self.max_loss_per_trade = 0.02  # 2% por trade
        self.min_profit_target = 0.01    # 1% alvo mínimo
        
    def calculate_option_parameters(self, signal: int, current_price: float) -> Dict:
        """
        Calcula parâmetros para operações com opções
        
        Parameters:
        -----------
        signal: int
            1 para CALL (alta), -1 para PUT (baixa)
        current_price: float
            Preço atual do WDO
            
        Returns:
        --------
        Dict com parâmetros da operação
        """
        if signal == 1:  # CALL - Expectativa de ALTA
            strike_price = self._calculate_call_strike(current_price)
            stop_loss = current_price * 0.997  # Stop 0.3% abaixo
            take_profit = current_price * 1.005  # Alvo 0.5% acima
            
        else:  # PUT - Expectativa de BAIXA
            strike_price = self._calculate_put_strike(current_price)
            stop_loss = current_price * 1.003  # Stop 0.3% acima
            take_profit = current_price * 0.995  # Alvo 0.5% abaixo
            
        return {
            'option_type': 'CALL' if signal == 1 else 'PUT',
            'strike_price': strike_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'position_size': self._calculate_position_size(current_price)
        }
    
    def _calculate_call_strike(self, current_price: float) -> float:
        """Calcula strike price ideal para CALL"""
        # Arredonda para o strike mais próximo
        # WDO tem strikes de 5 em 5 pontos
        return np.ceil(current_price / 5) * 5
    
    def _calculate_put_strike(self, current_price: float) -> float:
        """Calcula strike price ideal para PUT"""
        return np.floor(current_price / 5) * 5
    
    def _calculate_position_size(self, current_price: float) -> int:
        """Calcula tamanho da posição baseado no risco"""
        account_value = 100000  # Exemplo - deve vir da configuração
        risk_per_trade = account_value * self.max_loss_per_trade
        contract_value = current_price * 10  # Cada ponto = R$ 10
        
        return max(1, int(risk_per_trade / contract_value))
    
    def validate_trade(self, signal: int, current_price: float, 
                      volatility: float) -> Tuple[bool, str]:
        """Valida se o trade deve ser executado"""
        hour = pd.Timestamp.now().hour
        
        # Regras de validação
        if hour < 9 or hour > 17:
            return False, "Fora do horário de trading"
            
        if volatility > self.data['Close'].pct_change().std() * 2:
            return False, "Volatilidade muito alta"
            
        if self._count_daily_trades() >= self.max_trades_per_day:
            return False, "Limite diário de trades atingido"
            
        return True, "Trade válido"
    
    def _count_daily_trades(self) -> int:
        """Conta número de trades no dia"""
        today = pd.Timestamp.now().date()
        daily_trades = self.data[self.data.index.date == today]
        return len(daily_trades[daily_trades['Volume'] > 0])