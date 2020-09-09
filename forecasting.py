"""
This file will predict next 30 days sold and profit using machine learning models and techniques
Models Used For Forecasting Are : Arima and Gaussian Process
Technique Used To Fill Missing Or Error Data Is Base Value
"""
# ========== Try Block To Import Files ==========
# This try block will check for all files that are being importing.
# If any of file is missing it terminates the app
try:
    from statsmodels.tsa.arima_model import ARIMA  # ARIMA Model for time series predictions
    from statsmodels.tools.sm_exceptions import ConvergenceWarning, HessianInversionWarning
    from sklearn.gaussian_process import GaussianProcessRegressor  # Gaussian Model for profit predictions
    import pandas as pd
    import numpy as np
    from sqlalchemy import create_engine
    from bootstrap import params
    from models import SellingByDate, ForecastData, TopProducts
    from random import seed, uniform
    from datetime import date, timedelta
    import warnings
except FileExistsError or FileNotFoundError or ImportError:
    print("Please Check For Forecasting File Or Check Modules(statsmodels, sklearn etc) Are Installed Or Not")
    exit()
# ===============================================
engine = create_engine(params["local_host_uri"])  # url of database to get previous data
rounded_forecast_sold = list()  # forecast sold values list
rounded_forecast_profit = list()  # forecast profit values list


# This Function Will Forecast Next 30 Days Sold
def forecast_sold():
    data = pd.read_sql_table("selling_by_date", columns=["date", "total_sold"], con=engine)
    if len(data) < 10:
        return False
    data["date"] = data["date"].str.replace("-", "").astype(int)
    x = np.array(data.values)
    x = x.astype(float)
    percent_data = int(len(data) * (7/10))
    train = x[0:percent_data]
    train = np.array(train).reshape(-1)
    history = [y for y in train]
    p = 0  # number of auto regressive terms,
    d = 1  # number of nonseasonal differences
    q = 0  # number of lagged forecast errors
    un_rounded_forecast_sold = list()
    un_rounded_forecast_sold.clear()
    max_value, min_value = SellingByDate.get_min_max_sold()
    # We will predict values 1. (until list get fill up to 30 values) or 2. (d get to 3 as d = 3 is not supported)
    while d < 3 or len(un_rounded_forecast_sold) >= 15:
        try:
            model = ARIMA(history, order=(p, d, q))
            model_fit = model.fit(disp=0)
            forecast = model_fit.forecast(steps=15)[0]
            for value in forecast:
                if value >= int(min_value.total_sold):
                    if value <= int(max_value.total_sold):
                        un_rounded_forecast_sold.append(value)
            if len(un_rounded_forecast_sold) >= 15:
                break
            else:  # changing values in if else to get better forecast results
                if p == 1 or p == 0:
                    p = p + 1
                elif p == 2:
                    d = d + 1
                elif p == 2 and d == 2:
                    p = p + 1
                elif p == 3 and d == 2:
                    q = q + 1
                elif p == 3 and d == 2 and q == 1:
                    q = q + 1
                else:
                    break
        except ValueError or RuntimeWarning:
            if p == 1 or p == 0:  # changing values in if else to get better forecast results
                p = p + 1
            elif p == 2:
                d = d + 1
            elif p == 2 and d == 2:
                p = p + 1
            elif p == 3 and d == 2:
                q = q + 1
            elif p == 3 and d == 2 and q == 1:
                q = q + 1
            else:
                break

    # If un_rounded_forecast_sold contain values more then or less then 30
    # If un_rounded_forecast_sold contain values less then 30 we will fill remaining values
    if len(un_rounded_forecast_sold) < 15:
        up_to = 15 - len(un_rounded_forecast_sold)
        no = list()  # The random uniform values list
        for i in range(1):
            seed(1)
            no = [uniform(min_value.total_sold, max_value.total_sold) for _ in range(up_to)]
        for value in no:
            un_rounded_forecast_sold.append(value)

    # ======================================================================================

    # If un_rounded_forecast_sold contain values more then 30 we will remove extra values
    elif len(un_rounded_forecast_sold) > 15:
        while len(un_rounded_forecast_sold) == 15:
            un_rounded_forecast_sold.pop()
    # ====================================================================================

    # ===================================================================
    # un_rounded_forecast_sold list contain float digits up to many decimal points we will filter it with only 2 points
    for value in un_rounded_forecast_sold:
        value = round(value, 0)
        rounded_forecast_sold.append(value)

    return True
    # =================================================================================================================

# =========================================== Function forecast_sold ends here ====================================


# Function To Predict Profit On Basis Of Forecast Sold
def forecast_profit():
    data = SellingByDate.get_sell_records_by_date()
    x_train_data = list()
    y_train_data = list()
    x_forecast_values = list()
    for value in rounded_forecast_sold:
        x_forecast_values.append([value])
    for value in data:
        x_train_data.append([float(value.total_sold)])
        y_train_data.append([int(value.gen_profit)])
    if len(x_train_data) != len(y_train_data) or len(x_train_data) < 10:
        return False

    gp = GaussianProcessRegressor()
    gp.fit(x_train_data, y_train_data)
    un_rounded_y_predicted = gp.predict(x_forecast_values)
    for values in un_rounded_y_predicted:
        for value in values:
            value = round(value, 0)
            rounded_forecast_profit.append(value)

    return True

# ============================================================


# This Function will get forecast data from both function check some validations and return the data
def generate_forecast_data():
    # To Ignore Warnings
    np.seterr(divide='ignore', invalid='ignore')  # to ignore division by zero
    warnings.simplefilter('ignore', ConvergenceWarning)
    warnings.simplefilter('ignore', HessianInversionWarning)  # LikelyHood In Training Data
    # =================
    rounded_forecast_profit.clear()
    rounded_forecast_sold.clear()
    forecast_sold_func_data = forecast_sold()
    if forecast_sold_func_data is False:
        return False
    else:
        forecast_profit_func_data = forecast_profit()
        if forecast_profit_func_data is False:
            return False
        else:
            # Saving Forecast Data Into Database
            for_stats_data = pd.read_sql_table("selling_by_date", columns=["date", "total_sold"], con=engine)
            ForecastData.save_next_forecast(rounded_forecast_sold, rounded_forecast_profit)
            stats = [for_stats_data["total_sold"].count(), for_stats_data["total_sold"].max(),
                     for_stats_data["total_sold"].mean(), for_stats_data["total_sold"].min(),
                     int(for_stats_data["total_sold"].count() * (7 / 10)), for_stats_data["total_sold"].median(),
                     for_stats_data["total_sold"].std()]
            return stats

# ===================================================================================================
