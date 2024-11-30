from setuptools import setup, find_packages

setup(
    name='mini-dolar-strategy',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pandas>=1.5.0',
        'numpy>=1.21.0',
        'scikit-learn>=1.0.0',
        'tensorflow>=2.10.0',
        'yfinance>=0.1.70',
        'plotly>=5.0.0'
    ]
)