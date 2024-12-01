# analysis/performance.py
import pandas as pd
import numpy as np
from typing import Dict
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class PerformanceAnalyzer:
    def __init__(self, results: pd.DataFrame, strategy_data: pd.DataFrame):
        self.results = results
        self.strategy_data = strategy_data  # Adicionando dados da estratégia

    def analyze(self) -> Dict:
        """Calculate and return performance metrics"""
        try:
            # Garantir que estamos trabalhando com números
            equity = self.results['equity'].astype(float)
            returns = self.results['strategy_returns'].astype(float).fillna(0)
            
            # Calcular retornos
            initial_equity = equity.iloc[0]
            final_equity = equity.iloc[-1]
            
            if initial_equity > 0:  # Evitar divisão por zero
                total_return = ((final_equity / initial_equity) - 1) * 100
            else:
                total_return = 0
                
            metrics = {
                'Initial Capital': f"${initial_equity:,.2f}",
                'Final Capital': f"${final_equity:,.2f}",
                'Total Return': f"{total_return:.2f}%",
                'Annual Return': f"{self._calculate_annual_return(total_return):.2f}%",
                'Sharpe Ratio': f"{self._calculate_sharpe_ratio(returns):.2f}",
                'Max Drawdown': f"{self._calculate_max_drawdown():.2f}%",
                'Win Rate': f"{self._calculate_win_rate(returns):.2f}%",
                'Total Trades': f"{self._calculate_total_trades():,d}",
                'Profit Factor': f"{self._calculate_profit_factor(returns):.2f}",
                'Daily Volatility': f"{returns.std() * np.sqrt(252) * 100:.2f}%"
            }
            
            return metrics
            
        except Exception as e:
            print(f"Erro no cálculo de métricas: {str(e)}")
            return self._get_default_metrics()
    
    def _calculate_annual_return(self, total_return: float) -> float:
        years = len(self.results) / 252  # 252 dias úteis no ano
        return total_return / years if years > 0 else 0
    
    def _calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        if returns.std() == 0 or returns.empty:
            return 0
        return np.sqrt(252) * returns.mean() / returns.std()
    
    def _calculate_max_drawdown(self) -> float:
        equity = self.results['equity'].astype(float)
        peak = equity.expanding().max()
        drawdown = ((equity - peak) / peak) * 100
        return drawdown.min()
    
    def _calculate_win_rate(self, returns: pd.Series) -> float:
        if returns.empty:
            return 0
        winning_trades = len(returns[returns > 0])
        total_trades = len(returns[returns != 0])
        return (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    def _calculate_total_trades(self) -> int:
        position_changes = self.results['position'].diff()
        return len(position_changes[position_changes != 0])
    
    def _calculate_profit_factor(self, returns: pd.Series) -> float:
        if returns.empty:
            return 0
        gains = returns[returns > 0].sum()
        losses = abs(returns[returns < 0].sum())
        return gains / losses if losses != 0 else 0
    
    def _get_default_metrics(self) -> Dict:
        return {
            'total_return': '0.00%',
            'annual_return': '0.00%',
            'sharpe_ratio': '0.00',
            'max_drawdown': '0.00%',
            'win_rate': '0.00%',
            'total_trades': '0',
            'profit_factor': '0.00'
        }
    def plot_results(self, strategy_name: str):
        """Plot backtest results"""
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            subplot_titles=('Price and Signals', 'Equity Curve', 'Drawdown'),
            vertical_spacing=0.05,
            row_heights=[0.5, 0.3, 0.2]
        )

        # Price chart
        fig.add_trace(go.Candlestick(
            x=self.strategy_data.index,
            open=self.strategy_data['Open'],
            high=self.strategy_data['High'],
            low=self.strategy_data['Low'],
            close=self.strategy_data['Close'],
            name='Price'
        ), row=1, col=1)

        # Adicionar sinais ao gráfico de preço
        buy_signals = self.results[self.results['position'] == 1].index
        sell_signals = self.results[self.results['position'] == -1].index

        if len(buy_signals) > 0:
            fig.add_trace(go.Scatter(
                x=buy_signals,
                y=self.strategy_data.loc[buy_signals, 'Low'] * 0.999,
                mode='markers',
                marker=dict(symbol='triangle-up', size=10, color='green'),
                name='Buy Signal'
            ), row=1, col=1)

        if len(sell_signals) > 0:
            fig.add_trace(go.Scatter(
                x=sell_signals,
                y=self.strategy_data.loc[sell_signals, 'High'] * 1.001,
                mode='markers',
                marker=dict(symbol='triangle-down', size=10, color='red'),
                name='Sell Signal'
            ), row=1, col=1)

        # Equity curve
        fig.add_trace(go.Scatter(
            x=self.results.index,
            y=self.results['equity'],
            name='Equity',
            line=dict(color='green')
        ), row=2, col=1)

        # Drawdown
        drawdown = ((self.results['equity'] - self.results['equity'].cummax()) / 
                   self.results['equity'].cummax() * 100)
        fig.add_trace(go.Scatter(
            x=self.results.index,
            y=drawdown,
            name='Drawdown',
            fill='tozeroy',
            line=dict(color='red')
        ), row=3, col=1)

        # Update layout
        fig.update_layout(
            title=f'{strategy_name} Backtest Results',
            height=1000,
            showlegend=True,
            xaxis3_title='Date',
            yaxis_title='Price',
            yaxis2_title='Equity',
            yaxis3_title='Drawdown %'
        )

        fig.show()

    def detailed_analysis(self) -> Dict:
        """Análise detalhada das operações"""
        try:
            trades = self._extract_trades()
            
            analysis = {
                'Trade Analysis': {
                    'Average Trade Duration': self._calculate_trade_duration(trades),
                    'Best Trade': f"${trades['profit'].max():.2f}",
                    'Worst Trade': f"${trades['profit'].min():.2f}",
                    'Average Profit': f"${trades['profit'].mean():.2f}",
                    'Average Loss': f"${trades['profit'][trades['profit'] < 0].mean():.2f}",
                    'Profit Distribution': self._analyze_profit_distribution(trades),
                    'Time Analysis': self._analyze_time_periods(trades),
                },
                'Risk Analysis': {
                    'Average Drawdown': f"{self._calculate_avg_drawdown():.2f}%",
                    'Recovery Factor': self._calculate_recovery_factor(),
                    'Risk-Adjusted Return': self._calculate_risk_adjusted_return(),
                    'Win Streak': self._calculate_streaks()['win'],
                    'Loss Streak': self._calculate_streaks()['loss'],
                }
            }
            
            return analysis
        except Exception as e:
            print(f"Erro na análise detalhada: {str(e)}")
            return {}

    def _extract_trades(self) -> pd.DataFrame:
        """Extrai informações detalhadas das operações"""
        trades = []
        position = 0
        entry_price = 0
        entry_time = None
        
        for idx, row in self.results.iterrows():
            if row['position'] != position:
                if position != 0:  # Fechando posição
                    profit = (row['close'] - entry_price) * position
                    trades.append({
                        'entry_time': entry_time,
                        'exit_time': idx,
                        'duration': (idx - entry_time).total_seconds() / 3600,  # em horas
                        'entry_price': entry_price,
                        'exit_price': row['close'],
                        'position': position,
                        'profit': profit
                    })
                if row['position'] != 0:  # Abrindo nova posição
                    position = row['position']
                    entry_price = row['close']
                    entry_time = idx
                else:
                    position = 0
                    
        return pd.DataFrame(trades)