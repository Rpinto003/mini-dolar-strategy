
# Mini Dolar Strategy

This project aims to develop a trading strategy for the mini dolar (WDO) futures contract on the Brazilian stock exchange.

## Current Strategy

The current strategy is based on a machine learning model implemented in the `ml_strategy` directory. The main components are:

1. **Data Processor**: Responsible for loading and processing the input data.
2. **Feature Engineering**: Implements feature engineering to prepare the input data.
3. **Model**: Implements the machine learning model, including the neural network architecture, training, and inference.
4. **Risk Manager**: Contains logic to manage the risk of the trading strategy.

The strategy uses a multi-class classification approach to predict whether the next price movement will be a CALL, PUT, or remain neutral. The model is trained using LightGBM and cross-validation.

## Proposed Improvements

After analyzing the current implementation, here are some suggestions for improvements:

1. **Hyperparameter Optimization**: Implement a hyperparameter search to find the optimal parameters for the LightGBM model, such as learning rate, max depth, and number of leaves.
2. **Additional Features**: Incorporate more features into the model, such as macroeconomic indicators, sentiment analysis, or information about related options.
3. **Binary Classification vs. Multi-Class**: Compare the current multi-class classification approach with a binary classification (CALL vs. PUT) to see which provides better performance.
4. **Feature Importance Analysis**: Perform a feature importance analysis to identify the key drivers of the model and guide future improvements.
5. **Ensemble Models**: Experiment with combining multiple machine learning models (e.g., LightGBM, XGBoost, Random Forest) in an ensemble to improve the predictive capability.

These improvements can help enhance the machine learning strategy and the identification of CALL and PUT opportunities.

## Backtest and Performance Analysis

The project includes a backtest module and a performance analysis component. The backtest results and performance metrics are displayed in the main script.

## Next Steps

1. Implement the proposed improvements to the machine learning strategy.
2. Expand the strategy module to include additional trading strategies, such as rule-based or hybrid approaches.
3. Conduct thorough testing and evaluation of the strategies using the backtest and performance analysis tools.
4. Document the trading strategies, their rationale, and the results of the backtesting.
5. Continuously monitor and update the strategies as market conditions and data evolve.

