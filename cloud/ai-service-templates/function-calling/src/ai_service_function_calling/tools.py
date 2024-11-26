import numpy as np
import statsmodels.api as sm
from langchain_core.tools import tool
from scipy.stats import shapiro, pearsonr
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson


@tool(parse_docstring=True)
def ordinary_least_squared_regression(exog: list, endog: list) -> str:
    """
    Fits an Ordinary Least Squares Linear Regression model to the provided data.

    Args:
        exog: List of explanatory variables.
        endog: List of dependent (response) variables.

    Returns:
        Summary of the OLS regression if all assumptions are satisfied.
    """
    # Add a constant to exogenous variables
    exog = sm.add_constant(exog)

    # Fit the OLS model
    model = sm.OLS(endog, exog).fit()
    return model.summary().as_text()


@tool(parse_docstring=True)
def pearson_correlation(exog: list, endog: list) -> dict:
    """
    Computes the Pearson correlation coefficient to check for linearity.

    Args:
        exog: List of explanatory variables.
        endog: List of dependent (response) variables.

    Returns:
        A dictionary containing the correlation coefficient and p-value.
    """
    exog = np.array(exog)
    endog = np.array(endog)
    correlation, p_value = pearsonr(exog, endog)
    return {"correlation_coefficient": correlation, "p_value": p_value}


@tool(parse_docstring=True)
def check_residuals_normality(exog: list, endog: list) -> bool:
    """
    Checks if the residuals of a regression model follow a normal distribution using the Shapiro-Wilk test.

    Args:
        exog: List of explanatory variables.
        endog: List of dependent variable values.

    Returns:
        True if residuals are normally distributed (p-value > 0.05), False otherwise.
    """
    exog = sm.add_constant(exog)
    model = sm.OLS(endog, exog).fit()
    residuals = model.resid
    stat, p_value = shapiro(residuals)
    return p_value > 0.05


@tool(parse_docstring=True)
def data_independence_test(exog: list, endog: list) -> bool:
    """
    Checks if the data points are independent using the Durbin-Watson test.

    Args:
        exog: List of explanatory variables.
        endog: List of dependent (response) variables.

    Returns:
      True if data points are independent (Durbin-Watson statistic between 1.5 and 2.5),
      False otherwise.
    """
    # Perform Durbin-Watson test on the residuals of the model
    exog = sm.add_constant(exog)
    model = sm.OLS(endog, exog).fit()
    dw_stat = durbin_watson(model.resid)

    # A Durbin-Watson statistic between 1.5 and 2.5 suggests no autocorrelation
    return 1.5 <= dw_stat <= 2.5


@tool(parse_docstring=True)
def homoscedasticity_tests(exog: list, endog: list) -> bool:
    """
    Performs a Breusch-Pagan test for homoscedasticity (equal variance).

    Args:
        exog: List of explanatory variables.
        endog: List of dependent (response) variables.

    Returns:
        True if homoscedasticity is satisfied (p-value > 0.05), False otherwise.
    """
    # Perform Breusch-Pagan test for heteroscedasticity
    exog = sm.add_constant(exog)
    model = sm.OLS(endog, exog).fit()
    bp_test_stat, bp_p_value, _, _ = het_breuschpagan(model.resid, model.model.exog)

    # If the p-value is greater than 0.05, we do not reject the null hypothesis of homoscedasticity
    return bp_p_value > 0.05
