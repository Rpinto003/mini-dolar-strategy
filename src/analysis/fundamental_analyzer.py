import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Tuple

class FundamentalAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Categorias de eventos
        self.event_categories = {
            'monetary_policy': [
                'taxa selic', 'copom', 'federal reserve', 'fomc',
                'taxa de juros', 'interest rate'
            ],
            'economic_data': [
                'pib', 'gdp', 'inflação', 'inflation', 'ipca',
                'desemprego', 'unemployment'
            ],
            'trade_balance': [
                'balança comercial', 'trade balance', 'exportações',
                'importações', 'exports', 'imports'
            ],
            'geopolitical': [
                'guerra', 'war', 'eleições', 'elections',
                'sanções', 'sanctions'
            ]
        }
        
        # Pesos para diferentes tipos de eventos
        self.event_weights = {
            'monetary_policy': 1.5,
            'economic_data': 1.2,
            'trade_balance': 1.0,
            'geopolitical': 0.8
        }
        
    def collect_news(self, start_date: str, end_date: str,
                     brave_api_key: str) -> pd.DataFrame:
        """Coleta notícias relevantes usando Brave API.
        
        Args:
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)
            brave_api_key: Chave da API do Brave
            
        Returns:
            DataFrame com notícias coletadas
        """
        from src.data.news_collector import NewsCollector
        
        collector = NewsCollector(brave_api_key)
        queries = [
            'dollar exchange rate',
            'USD BRL',
            'forex market',
            'central bank policy',
            'interest rates',
            'economic indicators'
        ]
        
        news_data = []
        for query in queries:
            results = collector.search_news(
                query=query,
                start_date=start_date,
                end_date=end_date
            )
            news_data.extend(results)
        
        return pd.DataFrame(news_data)
    
    def classify_news(self, news_df: pd.DataFrame) -> pd.DataFrame:
        """Classifica notícias por categoria.
        
        Args:
            news_df: DataFrame com notícias
            
        Returns:
            DataFrame com notícias classificadas
        """
        df = news_df.copy()
        
        def categorize_text(text: str) -> List[str]:
            text = text.lower()
            categories = []
            
            for category, keywords in self.event_categories.items():
                if any(keyword in text for keyword in keywords):
                    categories.append(category)
            
            return categories if categories else ['other']
        
        # Aplica categorização
        df['categories'] = df['title'].apply(categorize_text)
        
        return df
    
    def analyze_sentiment(self, news_df: pd.DataFrame) -> pd.DataFrame:
        """Analisa sentimento das notícias.
        
        Args:
            news_df: DataFrame com notícias
            
        Returns:
            DataFrame com sentimentos analisados
        """
        from transformers import pipeline
        
        df = news_df.copy()
        analyzer = pipeline('sentiment-analysis')
        
        def get_sentiment(text: str) -> Dict:
            try:
                result = analyzer(text[:512])[0]  # Limita tamanho do texto
                return {
                    'sentiment': result['label'],
                    'score': result['score']
                }
            except Exception as e:
                self.logger.error(f"Erro ao analisar sentimento: {str(e)}")
                return {'sentiment': 'NEUTRAL', 'score': 0.5}
        
        # Analisa sentimentos
        sentiments = df['title'].apply(get_sentiment)
        df['sentiment'] = sentiments.apply(lambda x: x['sentiment'])
        df['sentiment_score'] = sentiments.apply(lambda x: x['score'])
        
        return df
    
    def calculate_impact_score(self, news_df: pd.DataFrame) -> pd.DataFrame:
        """Calcula score de impacto das notícias.
        
        Args:
            news_df: DataFrame com notícias classificadas e analisadas
            
        Returns:
            DataFrame com scores de impacto
        """
        df = news_df.copy()
        
        def calculate_score(row: pd.Series) -> float:
            # Base score from sentiment
            base_score = row['sentiment_score']
            if row['sentiment'] == 'NEGATIVE':
                base_score = -base_score
            
            # Weight by category
            category_weight = max(
                self.event_weights.get(cat, 0.5)
                for cat in row['categories']
            )
            
            return base_score * category_weight
        
        df['impact_score'] = df.apply(calculate_score, axis=1)
        
        return df
    
    def correlate_with_price(self, news_df: pd.DataFrame,
                            price_df: pd.DataFrame,
                            window: str = '1D') -> pd.DataFrame:
        """Correlaciona notícias com movimentos de preço.
        
        Args:
            news_df: DataFrame com notícias e scores
            price_df: DataFrame com preços
            window: Janela de tempo para agregação
            
        Returns:
            DataFrame com correlações
        """
        # Agrupa scores de impacto por período
        news_df['date'] = pd.to_datetime(news_df['date'])
        daily_impact = news_df.groupby(
            pd.Grouper(key='date', freq=window)
        )['impact_score'].agg(['mean', 'count', 'sum']).fillna(0)
        
        # Calcula retornos
        price_df['returns'] = price_df['close'].pct_change()
        
        # Agrupa retornos no mesmo período
        price_returns = price_df.groupby(
            pd.Grouper(freq=window)
        )['returns'].sum()
        
        # Combina dados
        combined = pd.concat([daily_impact, price_returns], axis=1)
        combined = combined.dropna()
        
        # Calcula correlações
        correlations = {
            'impact_vs_returns': combined['sum'].corr(combined['returns']),
            'news_count_vs_volatility': combined['count'].corr(
                combined['returns'].abs()
            )
        }
        
        return combined, correlations
    
    def generate_signals(self, news_df: pd.DataFrame,
                        threshold: float = 0.5) -> pd.Series:
        """Gera sinais baseados na análise fundamentalista.
        
        Args:
            news_df: DataFrame com notícias analisadas
            threshold: Limite para geração de sinais
            
        Returns:
            Series com sinais (-1, 0, 1)
        """
        df = news_df.copy()
        
        # Agrupa scores por dia
        daily_scores = df.groupby(
            pd.Grouper(key='date', freq='1D')
        )['impact_score'].sum()
        
        # Gera sinais
        signals = pd.Series(0, index=daily_scores.index)
        signals[daily_scores > threshold] = 1
        signals[daily_scores < -threshold] = -1
        
        return signals