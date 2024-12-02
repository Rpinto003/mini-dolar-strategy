import pytest
import pandas as pd
import numpy as np
from src.evaluation.model_validation import TimeSeriesValidator

class MockModel:
    def fit(self, X, y):
        pass
        
    def predict(self, X):
        return np.random.randn(len(X))

@pytest.fixture
def sample_data():
    dates = pd.date_range(start='2023-01-01', periods=252, freq='B')
    data = pd.DataFrame({
        'Close': np.random.randn(252).cumsum(),
        'Feature1': np.random.randn(252),
        'Feature2': np.random.randn(252),
        'Target': np.random.randn(252)
    }, index=dates)
    return data

def test_generate_validation_splits(sample_data):
    validator = TimeSeriesValidator(n_splits=3, test_size=21)
    splits = validator.generate_validation_splits(sample_data)
    
    assert len(splits) == 3
    for split in splits:
        assert 'train' in split
        assert 'test' in split
        assert split['test']['end'] - split['test']['start'] == 21

def test_calculate_metrics(sample_data):
    validator = TimeSeriesValidator()
    returns = sample_data['Close'].pct_change().dropna()
    
    metrics = validator.calculate_metrics(
        y_true=np.random.randn(100),
        y_pred=np.random.randn(100),
        returns=returns
    )
    
    expected_metrics = ['rmse', 'mae', 'total_return', 'annual_return',
                       'volatility', 'sharpe_ratio', 'sortino_ratio',
                       'max_drawdown']
    
    for metric in expected_metrics:
        assert metric in metrics
        assert isinstance(metrics[metric], float)

def test_validate_model(sample_data):
    validator = TimeSeriesValidator(n_splits=2, test_size=21)
    model = MockModel()
    
    results = validator.validate_model(
        model=model,
        data=sample_data,
        feature_columns=['Feature1', 'Feature2'],
        target_column='Target'
    )
    
    assert isinstance(results, pd.DataFrame)
    assert len(results) == 2  # n_splits
    assert 'sharpe_ratio' in results.columns
    assert 'sortino_ratio' in results.columns

def test_validation_report(sample_data, tmp_path):
    validator = TimeSeriesValidator(n_splits=2, test_size=21)
    model = MockModel()
    
    validator.validate_model(
        model=model,
        data=sample_data,
        feature_columns=['Feature1', 'Feature2'],
        target_column='Target'
    )
    
    report_path = tmp_path / "validation_report.html"
    validator.generate_validation_report(str(report_path))
    
    assert report_path.exists()
    with open(report_path) as f:
        content = f.read()
        assert "<h1>" in content
        assert "Estatísticas Gerais" in content