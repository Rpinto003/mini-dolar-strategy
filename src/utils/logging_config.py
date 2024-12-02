import logging
import logging.handlers
import os
from datetime import datetime
from typing import Dict, Optional
import json

class StrategyLogger:
    def __init__(self, log_dir: str = 'logs', max_bytes: int = 10485760,
                 backup_count: int = 5):
        """Inicializa configurador de logging.
        
        Args:
            log_dir: Diretório para armazenar logs
            max_bytes: Tamanho máximo do arquivo de log antes de rotacionar
            backup_count: Número de backups a manter
        """
        self.log_dir = log_dir
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        # Cria diretório de logs se não existir
        os.makedirs(log_dir, exist_ok=True)
        
        # Define formato do log
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
    def setup_logger(self, name: str, level: int = logging.INFO) -> logging.Logger:
        """Configura logger com handlers para arquivo e console.
        
        Args:
            name: Nome do logger
            level: Nível de logging
            
        Returns:
            logging.Logger: Logger configurado
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Evita duplicação de handlers
        if not logger.handlers:
            # Handler para arquivo com rotação
            log_file = os.path.join(
                self.log_dir,
                f"{name}_{datetime.now():%Y%m%d}.log"
            )
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.max_bytes,
                backupCount=self.backup_count
            )
            file_handler.setFormatter(self.formatter)
            logger.addHandler(file_handler)
            
            # Handler para console
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(self.formatter)
            logger.addHandler(console_handler)
        
        return logger

class StrategyMonitor:
    def __init__(self, metrics_file: str = 'metrics.json'):
        """Inicializa monitor de estratégia.
        
        Args:
            metrics_file: Arquivo para armazenar métricas
        """
        self.metrics_file = metrics_file
        self.metrics = self._load_metrics()
        
        # Configura logger
        self.logger = StrategyLogger().setup_logger('monitor')
        
    def _load_metrics(self) -> Dict:
        """Carrega métricas do arquivo.
        
        Returns:
            Dict: Métricas carregadas ou dicionário vazio
        """
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def _save_metrics(self):
        """Salva métricas no arquivo."""
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=4)
    
    def record_metric(self, name: str, value: float,
                      timestamp: Optional[str] = None):
        """Registra uma métrica.
        
        Args:
            name: Nome da métrica
            value: Valor da métrica
            timestamp: Timestamp opcional (usa atual se não fornecido)
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
            
        if name not in self.metrics:
            self.metrics[name] = []
            
        self.metrics[name].append({
            'timestamp': timestamp,
            'value': value
        })
        
        self._save_metrics()
        self.logger.info(f"Métrica registrada: {name}={value}")
    
    def get_metric_history(self, name: str) -> list:
        """Retorna histórico de uma métrica.
        
        Args:
            name: Nome da métrica
            
        Returns:
            list: Histórico da métrica
        """
        return self.metrics.get(name, [])
    
    def alert_threshold(self, metric_name: str, threshold: float,
                       comparison: str = 'greater'):
        """Verifica se métrica ultrapassa threshold.
        
        Args:
            metric_name: Nome da métrica
            threshold: Valor limite
            comparison: Tipo de comparação ('greater' ou 'less')
        """
        history = self.get_metric_history(metric_name)
        if not history:
            return
            
        last_value = history[-1]['value']
        
        if comparison == 'greater' and last_value > threshold:
            self.logger.warning(
                f"Alerta: {metric_name} ({last_value}) acima do limite ({threshold})"
            )
        elif comparison == 'less' and last_value < threshold:
            self.logger.warning(
                f"Alerta: {metric_name} ({last_value}) abaixo do limite ({threshold})"
            )
    
    def plot_metric(self, metric_name: str):
        """Plota evolução de uma métrica.
        
        Args:
            metric_name: Nome da métrica
        """
        import matplotlib.pyplot as plt
        from matplotlib.dates import DateFormatter
        import pandas as pd
        
        history = self.get_metric_history(metric_name)
        if not history:
            self.logger.warning(f"Sem dados para métrica {metric_name}")
            return
            
        df = pd.DataFrame(history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        plt.figure(figsize=(12, 6))
        plt.plot(df['timestamp'], df['value'])
        plt.title(f'Evolução da Métrica: {metric_name}')
        plt.xlabel('Data')
        plt.ylabel('Valor')
        plt.grid(True)
        
        # Formata eixo x
        plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.show()