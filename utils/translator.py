"""
Translation module for converting strategy analysis and documentation to Brazilian Portuguese.
"""
from typing import Dict, Any, Union

class Translator:
    def __init__(self):
        self.translations = {
            # Strategy terms
            'Buy': 'Compra',
            'Sell': 'Venda',
            'Hold': 'Manter',
            'Entry': 'Entrada',
            'Exit': 'Saída',
            'Stop Loss': 'Stop Loss',
            'Take Profit': 'Realização de Lucro',
            'Position': 'Posição',
            
            # Performance metrics
            'Total Return': 'Retorno Total',
            'Annualized Return': 'Retorno Anualizado',
            'Sharpe Ratio': 'Índice Sharpe',
            'Maximum Drawdown': 'Máxima Drawdown',
            'Win Rate': 'Taxa de Acerto',
            'Profit Factor': 'Fator de Lucro',
            'Average Win': 'Ganho Médio',
            'Average Loss': 'Perda Média',
            
            # Risk metrics
            'Volatility': 'Volatilidade',
            'Value at Risk': 'Valor em Risco',
            'Expected Shortfall': 'Perda Esperada',
            'Kelly Criterion': 'Critério Kelly',
            
            # Technical indicators
            'Moving Average': 'Média Móvel',
            'Relative Strength Index': 'Índice de Força Relativa',
            'MACD': 'MACD',
            'Bollinger Bands': 'Bandas de Bollinger',
            'Average True Range': 'Range Médio Verdadeiro',
            
            # Time periods
            'Daily': 'Diário',
            'Weekly': 'Semanal',
            'Monthly': 'Mensal',
            'Yearly': 'Anual',
            
            # General terms
            'Strategy': 'Estratégia',
            'Analysis': 'Análise',
            'Results': 'Resultados',
            'Performance': 'Desempenho',
            'Risk': 'Risco',
            'Trading': 'Negociação',
            'Portfolio': 'Carteira',
            'Market': 'Mercado',
            'Trend': 'Tendência',
            'Signal': 'Sinal',
        }
        
    def translate(self, text: str) -> str:
        """Translate a single text string to Portuguese"""
        for eng, port in self.translations.items():
            text = text.replace(eng, port)
        return text
    
    def translate_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate dictionary keys and string values to Portuguese"""
        translated = {}
        for key, value in data.items():
            translated_key = self.translate(key)
            if isinstance(value, str):
                translated[translated_key] = self.translate(value)
            elif isinstance(value, dict):
                translated[translated_key] = self.translate_dict(value)
            else:
                translated[translated_key] = value
        return translated
    
    def translate_performance_report(self, report: Dict[str, Union[float, str]]) -> Dict[str, Union[float, str]]:
        """Translate a performance report to Portuguese"""
        return self.translate_dict(report)
    
    def translate_risk_report(self, report: Dict[str, Union[float, str]]) -> Dict[str, Union[float, str]]:
        """Translate a risk analysis report to Portuguese"""
        return self.translate_dict(report)
    
    def translate_strategy_description(self, description: str) -> str:
        """Translate strategy description to Portuguese"""
        return self.translate(description)
    
    def translate_technical_documentation(self, documentation: str) -> str:
        """Translate technical documentation to Portuguese"""
        return self.translate(documentation)