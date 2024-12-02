import pandas as pd
import requests
from datetime import datetime, timedelta
import logging

class EconomicDataCollector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_urls = {
            'bcb': 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados',
            'fred': 'https://api.stlouisfed.org/fred/series/observations'
        }
        
        # Códigos das séries do BCB
        self.bcb_series = {
            'selic': 432,      # Taxa SELIC
            'ipca': 433,       # IPCA
            'cambio': 1        # Taxa de Câmbio
        }

    def fetch_bcb_data(self, series_code: int, start_date: str, end_date: str) -> pd.DataFrame:
        """Busca dados do Banco Central do Brasil.
        
        Args:
            series_code: Código da série temporal no BCB
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)
        """
        try:
            url = self.base_urls['bcb'].format(series_code)
            params = {
                'formato': 'json',
                'dataInicial': start_date.replace('-', ''),
                'dataFinal': end_date.replace('-', '')
            }
            
            response = requests.get(url, params=params)
            if response.ok:
                data = response.json()
                df = pd.DataFrame(data)
                df['data'] = pd.to_datetime(df['data'])
                df = df.set_index('data')
                return df
            else:
                self.logger.warning(f"Erro ao coletar dados do BCB: {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Erro ao coletar dados do BCB: {str(e)}")
            return pd.DataFrame()

    def fetch_fred_data(self, series_id: str, api_key: str,
                       start_date: str, end_date: str) -> pd.DataFrame:
        """Busca dados do Federal Reserve Economic Data (FRED)."""
        try:
            url = self.base_urls['fred']
            params = {
                'series_id': series_id,
                'api_key': api_key,
                'file_type': 'json',
                'observation_start': start_date,
                'observation_end': end_date
            }
            
            response = requests.get(url, params=params)
            if response.ok:
                data = response.json()['observations']
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
                return df
            else:
                self.logger.warning(f"Erro ao coletar dados do FRED: {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Erro ao coletar dados do FRED: {str(e)}")
            return pd.DataFrame()

    def collect_all_indicators(self, start_date: str, end_date: str,
                             fred_api_key: str = None) -> dict:
        """Coleta todos os indicadores configurados."""
        data = {}
        
        # Coleta dados do BCB
        for name, code in self.bcb_series.items():
            df = self.fetch_bcb_data(code, start_date, end_date)
            if not df.empty:
                data[f'bcb_{name}'] = df
                self.logger.info(f"Dados do BCB coletados: {name}")
        
        # Coleta dados do FRED se a API key estiver disponível
        if fred_api_key:
            fred_series = {
                'fed_rate': 'DFF',  # Federal Funds Rate
                'gdp': 'GDP',       # GDP
                'cpi': 'CPIAUCSL'   # Consumer Price Index
            }
            
            for name, series_id in fred_series.items():
                df = self.fetch_fred_data(series_id, fred_api_key, start_date, end_date)
                if not df.empty:
                    data[f'fred_{name}'] = df
                    self.logger.info(f"Dados do FRED coletados: {name}")
        
        return data

def main():
    """Função principal para teste."""
    collector = EconomicDataCollector()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Coleta dados (exemplo usando apenas BCB inicialmente)
    data = collector.collect_all_indicators(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    
    print("\nDados coletados:")
    for name, df in data.items():
        print(f"\n{name}:")
        print(df.head())

if __name__ == '__main__':
    main()