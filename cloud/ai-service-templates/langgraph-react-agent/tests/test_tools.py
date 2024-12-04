import pytest

from langgraph_react_agent import (
    ordinary_least_squared_regression,
    pearson_correlation,
    check_residuals_normality,
    data_independence_test,
    homoscedasticity_tests
)


@pytest.mark.parametrize("exog, endog", [
    (
            [1, 2, 3, 4, 5, 6, 7, 8],  # Integer values for X1
            [8.00, 10.58, 14.58, 18.67, 20.12, 23.34, 28.36, 30.77]  # Floats for Y1 with 2 decimal precision
    ),
    (
            [10.00, 11.43, 12.86, 14.29, 15.71, 17.14, 18.57, 20.00],  # Floats for X2 with 2 decimal precision
            [-0.94, -1.06, -5.21, -7.36, -8.09, -14.54, -16.31, -16.12]  # Floats for Y2 with 2 decimal precision
    )
])
class TestStatisticalTools:
    def test_ordinary_least_squared_regression(self, exog, endog):
        result = ordinary_least_squared_regression.run({"exog": exog, "endog": endog})
        assert "OLS Regression Results" in result  # Check if the result contains OLS summary

    def test_pearson_correlation(self, exog, endog):
        result = pearson_correlation.run({"exog": exog, "endog": endog})
        assert "correlation_coefficient" in result

    def test_check_residuals_normality(self, exog, endog):
        assert check_residuals_normality.run({"exog": exog, "endog": endog})

    def test_data_independence_test(self, exog, endog):
        assert data_independence_test.run({"exog": exog, "endog": endog})

    def test_homoscedasticity_tests(self, exog, endog):
        assert homoscedasticity_tests.run({"exog": exog, "endog": endog})
