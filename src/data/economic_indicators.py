import pandas as pd
import requests
from datetime import datetime, timedelta
import logging
import json

class EconomicDataCollector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configurações das séries do BCB
        self.bcb_series = {
            'SELIC': {
                'codigo': 432,
                'periodo_dias': 30,
                'descricao': 'Taxa SELIC'
            },
            'IPCA': {
                'codigo': 433,
                'periodo_dias': 180,  # Período maior para dados mensais
                'descricao': 'Índice de Preços ao Consumidor Amplo'
            },
            'Cambio': {
                'codigo': 1,
                'periodo_dias': 30,
                'descricao': 'Taxa de Câmbio - Livre - Dólar americano (compra)'
            }
        }
        
        # URLs base das APIs
        self.base_urls = {
            'bcb': 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados',
            'fred': 'https://api.stlouisfed.org/fred/series/observations'
        }

    def fetch_bcb_data(self, series_code: int, start_date: str, end_date: str) -> pd.DataFrame:
        """Busca dados do Banco Central do Brasil.
        
        Args:
            series_code: Código da série temporal no BCB
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)
        """
        try:
            # Converte as datas para o formato do BCB
            start = datetime.strptime(start_date, '%Y-%m-%d').strftime('%d/%m/%Y')
            end = datetime.strptime(end_date, '%Y-%m-%d').strftime('%d/%m/%Y')
            
<<<<<<< Updated upstream
            # Monta a URL
=======
>>>>>>> Stashed changes
            url = self.base_urls['bcb'].format(series_code)
            params = {
                'formato': 'json',
                'dataInicial': start,
                'dataFinal': end
<<<<<<< Updated upstream
            }
            headers = {
                'Accept': 'application/json'
            }
            
            self.logger.info(f"Buscando dados do BCB: série {series_code} de {start} até {end}")
            response = requests.get(url, params=params, headers=headers)
            
            if response.ok:
                try:
                    data = response.json()
                    if data:  # Verifica se há dados
                        df = pd.DataFrame(data)
                        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
                        df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
                        df = df.set_index('data')
                        self.logger.info(f"Dados coletados com sucesso: {len(df)} registros")
                        return df
                    
                except json.JSONDecodeError:
                    # Tenta URL alternativa para últimos dados
                    alt_url = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series_code}/dados/ultimos/30'
                    alt_response = requests.get(alt_url, params={'formato': 'json'})
                    
                    if alt_response.ok:
                        data = alt_response.json()
                        df = pd.DataFrame(data)
                        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
                        df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
                        df = df.set_index('data')
                        self.logger.info(f"Dados coletados via URL alternativa: {len(df)} registros")
                        return df
            
=======
            }
            
            self.logger.info(f"Buscando dados do BCB: {url}")
            response = requests.get(url, params=params)
            
            if response.ok:
                data = response.json()
                if data:  # Verifica se há dados
                    df = pd.DataFrame(data)
                    df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
                    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
                    df = df.set_index('data')
                    return df
                
>>>>>>> Stashed changes
            self.logger.warning(f"Erro na resposta do BCB: {response.status_code}")
            return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Erro ao coletar dados do BCB: {str(e)}")
            return pd.DataFrame()

    def fetch_fred_data(self, series_id: str, api_key: str,
                       start_date: str, end_date: str) -> pd.DataFrame:
        """Busca dados do Federal Reserve Economic Data (FRED).
        
        Args:
            series_id: ID da série no FRED
            api_key: Chave de API do FRED
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)
        """
        try:
            params = {
                'series_id': series_id,
                'api_key': api_key,
                'file_type': 'json',
                'observation_start': start_date,
                'observation_end': end_date
            }
            
            url = self.base_urls['fred']
            self.logger.info(f"Buscando dados do FRED: {series_id}")
            
            response = requests.get(url, params=params)
<<<<<<< Updated upstream
=======
            self.logger.info(f"Status FRED: {response.status_code}")
>>>>>>> Stashed changes
            
            if response.ok:
                data = response.json()
                if 'observations' in data:
                    df = pd.DataFrame(data['observations'])
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.set_index('date')
                    df['value'] = pd.to_numeric(df['value'], errors='coerce')
<<<<<<< Updated upstream
                    self.logger.info(f"Dados do FRED coletados: {len(df)} registros")
                    return df
            
            self.logger.warning(f"Erro na resposta FRED: {response.status_code}")
=======
                    return df
                else:
                    self.logger.warning("Resposta FRED sem observações")
            else:
                self.logger.warning(f"Erro na resposta FRED: {response.text}")
            
>>>>>>> Stashed changes
            return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Erro ao coletar dados do FRED: {str(e)}")
            return pd.DataFrame()

    def collect_all_indicators(self, start_date: str = None, end_date: str = None,
                             fred_api_key: str = None) -> dict:
        """Coleta todos os indicadores configurados.
        
        Args:
<<<<<<< Updated upstream
            start_date: Data inicial (YYYY-MM-DD), opcional
            end_date: Data final (YYYY-MM-DD), opcional
            fred_api_key: Chave de API do FRED, opcional
=======
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)
            fred_api_key: Chave de API do FRED (opcional)
>>>>>>> Stashed changes
            
        Returns:
            dict: Dicionário com DataFrames dos indicadores
        """
        data = {}
        end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        
        # Coleta dados do BCB
        for nome, config in self.bcb_series.items():
            # Calcula data inicial baseada no período configurado se não fornecida
            if not start_date:
                start = datetime.now() - timedelta(days=config['periodo_dias'])
                serie_start_date = start.strftime('%Y-%m-%d')
            else:
                serie_start_date = start_date
                
            df = self.fetch_bcb_data(
                series_code=config['codigo'],
                start_date=serie_start_date,
                end_date=end_date
            )
            
            if not df.empty:
<<<<<<< Updated upstream
                data[f'bcb_{nome.lower()}'] = df
                self.logger.info(
                    f"Dados do BCB coletados: {nome} - {len(df)} registros "
                    f"({df.index.min()} até {df.index.max()})"
                )
=======
                data[f'bcb_{name}'] = df
                self.logger.info(f"Dados do BCB coletados: {name} - {len(df)} registros")
>>>>>>> Stashed changes
        
        # Coleta dados do FRED se a API key estiver disponível
        if fred_api_key:
            fred_series = {
                'fed_rate': 'DFF',    # Federal Funds Rate
                'gdp': 'GDP',         # GDP
                'cpi': 'CPIAUCSL'     # Consumer Price Index
            }
            
            for name, series_id in fred_series.items():
                df = self.fetch_fred_data(
                    series_id=series_id,
                    api_key=fred_api_key,
                    start_date=start_date or (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                    end_date=end_date
                )
                
                if not df.empty:
                    data[f'fred_{name}'] = df
<<<<<<< Updated upstream
                    self.logger.info(
                        f"Dados do FRED coletados: {name} - {len(df)} registros "
                        f"({df.index.min()} até {df.index.max()})"
                    )
=======
                    self.logger.info(f"Dados do FRED coletados: {name} - {len(df)} registros")
>>>>>>> Stashed changes
        
        return data