# analysis/performance.py
import pandas as pd
import numpy as np
from typing import Dict
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class PerformanceAnalyzer:
    def __init__(self, results: pd.DataFrame, strategy_data: pd.DataFrame):
        self.results = results
        self.strategy_data = strategy_data
        self._prepare_results()

    def _prepare_results(self):
        """Prepara o DataFrame de resultados com cálculos iniciais"""
        try:
            INITIAL_CAPITAL = 100000.00  # Capital inicial definido
            print(f"\nDebug - Preparando resultados:")
            print(f"Capital Inicial Definido: ${INITIAL_CAPITAL:,.2f}")
            
            # Certificar que temos as colunas necessárias
            if 'signal' in self.results and 'price' in self.results:
                # Calcular retornos da estratégia
                self.results['strategy_returns'] = self.results['signal'].shift(1) * (
                    self.results['price'].pct_change()
                )
                
                # Calcular equity começando com o capital inicial
                self.results['equity'] = INITIAL_CAPITAL * (1 + self.results['strategy_returns']).cumprod()
                
                # Verificar os primeiros valores calculados
                print("\nDebug - Primeiros valores calculados:")
                print(f"Primeiros strategy_returns:\n{self.results['strategy_returns'].head()}")
                print(f"\nPrimeiros equity:\n{self.results['equity'].head()}")
                
                # Calcular posição
                self.results['position'] = self.results['signal'] * self.results['size']
                
            self.results = self.results.fillna(0)
            
        except Exception as e:
            print(f"Erro na preparação dos resultados: {str(e)}")

    def analyze(self) -> Dict:
        """Calculate and return performance metrics"""
        try:
            # Garantir que estamos trabalhando com números
            equity = self.results['equity'].astype(float)
            returns = self.results['strategy_returns'].astype(float).fillna(0)
            
            # Garantir que temos o capital inicial correto
            initial_equity = equity.iloc[0]  # Pega o primeiro valor da série equity
            final_equity = equity.iloc[-1]   # Pega o último valor
            
            # Verificar valores para debug
            print(f"\nDebug - Valores de Equity:")
            print(f"Primeiro valor equity: {initial_equity}")
            print(f"Último valor equity: {final_equity}")
            print(f"Primeiros 5 valores de equity:\n{equity.head()}")
            
            # Calcular retorno total
            total_return = ((final_equity / initial_equity) - 1) * 100 if initial_equity > 0 else 0
            
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

    def plot_results(self, strategy_name):
        """Plota os resultados do backtest"""
        try:
            # Criar gráfico com subplots
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.5, 0.25, 0.25],
                subplot_titles=("Price & Signals", "Equity Curve", "Drawdown")
            )

            # Adicionar candlesticks
            fig.add_trace(
                go.Candlestick(
                    x=self.strategy_data.index,
                    open=self.strategy_data['open'],
                    high=self.strategy_data['high'],
                    low=self.strategy_data['low'],
                    close=self.strategy_data['close'],
                    name="OHLC"
                ),
                row=1, col=1
            )

            # Adicionar sinais de compra/venda
            if 'signal' in self.results:
                longs = self.results[self.results['signal'] > 0]
                shorts = self.results[self.results['signal'] < 0]
                
                # Plotar pontos de entrada long
                fig.add_trace(
                    go.Scatter(
                        x=longs.index,
                        y=self.strategy_data.loc[longs.index, 'low'] * 0.999,
                        mode='markers',
                        marker=dict(symbol='triangle-up', size=10, color='green'),
                        name='Long Entry'
                    ),
                    row=1, col=1
                )
                
                # Plotar pontos de entrada short
                fig.add_trace(
                    go.Scatter(
                        x=shorts.index,
                        y=self.strategy_data.loc[shorts.index, 'high'] * 1.001,
                        mode='markers',
                        marker=dict(symbol='triangle-down', size=10, color='red'),
                        name='Short Entry'
                    ),
                    row=1, col=1
                )

            # Adicionar equity curve
            if 'equity' in self.results.columns:
                fig.add_trace(
                    go.Scatter(
                        x=self.results.index,
                        y=self.results['equity'],
                        name="Equity",
                        line=dict(color='blue')
                    ),
                    row=2, col=1
                )

            # Adicionar drawdown
            if 'equity' in self.results.columns:
                equity = self.results['equity']
                peak = equity.expanding().max()
                drawdown = ((equity - peak) / peak) * 100
                
                fig.add_trace(
                    go.Scatter(
                        x=self.results.index,
                        y=drawdown,
                        name="Drawdown",
                        line=dict(color='red')
                    ),
                    row=3, col=1
                )

            # Configurar layout
            fig.update_layout(
                title=f"{strategy_name} - Backtest Results",
                height=1000,
                showlegend=True,
                xaxis_rangeslider_visible=False
            )

            # Atualizar labels dos eixos
            fig.update_yaxes(title_text="Price", row=1, col=1)
            fig.update_yaxes(title_text="Equity ($)", row=2, col=1)
            fig.update_yaxes(title_text="Drawdown (%)", row=3, col=1)

            # Mostrar figura
            fig.show()
            
        except Exception as e:
            print(f"Erro na plotagem dos resultados: {e}")
            print(f"Detalhes do erro: {str(e)}")
    
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