# -*- coding: utf-8 -*-
"""
Created on Fri Feb 18 21:10:42 2022

@author: Nehal
"""

# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import accuracy_score

# =============================================================================
# Trial -- Using Rpy2 
# import plotly.express as px
# from statistics import mean
# from datetime import datetime
#
# import rpy2
# import rpy2.robjects as robjects
# import rpy2.robjects.packages as rpackages
# from rpy2.robjects.vectors import StrVector
# 
# ##Packages to try Rpy2
# packageNames = ('ggplot2', 'tidyverse','rayshader','rgl','DiagrammeR')
# utils = rpackages.importr('utils')
# utils.chooseCRANmirror(ind=1)
# 
# packnames_to_install = [a for a in packageNames if not rpackages.isinstalled(a)]
# 
# if len(packnames_to_install) > 0:
#     utils.install_packages(StrVector(packnames_to_install))
# =============================================================================

def app():
        
    # @cache
    @st.cache
    def load_data():
        datacsv = pd.read_csv("C:/Users/Nehal/JupyterNotebooks/decentraland.csv") #To load it from local
        #datacsv = pd.read_csv("decentraland.csv") #To load it from Github
        df = pd.DataFrame(datacsv)
        return df
    
    df = load_data()
    
    # only keep relevant columns
    df = df [['x','y','current_rate_pricemana','last_sale_timestamp',
                  'last_sale_transaction_timestamp', 'last_sale_transaction_created_timestamp']]
    
    # Create date field
    df['transaction_date'] = pd.to_datetime(df['last_sale_transaction_timestamp']).dt.date
    df['transaction_date_created'] = pd.to_datetime(df['last_sale_transaction_created_timestamp']).dt.date
    
    #### Calculate average price for a given area #### 
    # first add columns for ranges for average
    df['x_range_min'] = df["x"] - 20 
    df['x_range_max'] = df["x"] + 20 
    df['y_range_min'] = df["y"] - 20 
    df['y_range_max'] = df["y"] + 20 
    
    # Create function that calculates the average price
    def area_avg_price_fun_eth(x_min, x_max, y_min, y_max):
        area_avg_price = 'current_rate_pricemana'.mean([x_min,x_max,y_min,y_max])
        return area_avg_price
    
    #df['area_avg_price'] = df.apply(lambda row : area_avg_price_fun_eth(row['x_range_min'],row['x_range_max'], row['y_range_min'],row['y_range_max']), axis=1)
    range_max_min = ['x_range_min','x_range_max','y_range_min','y_range_max']
    area_avg_price = map(area_avg_price_fun_eth,range_max_min)
    
    #Temporary formula for USD Price
    df['area_avg_price'] = df['current_rate_pricemana']/ 2.96
    
    #Drop Duplicates
    df = df.drop_duplicates()
    
    ## Dashboard formatting in Streamlit ##
    st.sidebar.title('Decentraland')
    st.header("XG Boost Training Data")
    st.sidebar.header("Enter Values for Prediction")
    
    
    #Side slider bar
    x_range = st.sidebar.slider('X-Coordinate', value= [-200, 200])
    y_range = st.sidebar.slider('Y-Coordinate', value= [-200, 200])
    
    #Min and max values for Transaction Date Range
    oldest = df['transaction_date'].min() # Earliest date
    latest = df['transaction_date'].max() # Latest date
    
    ## Input fields
    date_transaction = st.sidebar.date_input('Transaction Date Range',latest,oldest,latest)
    area = st.sidebar.slider('Size of area to calculate `area_avg_price` (shown on map)', 0, 150, 20)
    mana_range = st.sidebar.slider('MANA price range:', value = [0,1000000],step = 10)
    usd_range = st.sidebar.slider('USD price range:', value = [0,1000000],step = 10)
    
    #Data filtering based on the input data and storing it into a different Dataframe
    df_dashboard = df.loc[(df['x'] >= x_range[0]) & (df['x'] <= x_range[1]) & 
                (df['y'] >= y_range[0]) & (df['y'] <= y_range[1]) & 
                (df['current_rate_pricemana'] >= mana_range[0]) &
                (df['current_rate_pricemana'] <= mana_range[1]) &
                (df['transaction_date'] <= date_transaction)]
    
    
    #XGBoost Algorithm
    
    # split data into X and y
    X = df_dashboard.iloc[:,0:3] # x, y, current_rate_pricemana
    Y = df_dashboard.iloc[:,12:13] #area_avg_price
    # split data into train and test sets
    seed = 7
    test_size = 0.33
    data_dmatrix = xgb.DMatrix(data=X,label=Y)
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=seed)
    # fit model no training data
    model = xgb.XGBRegressor(objective ='reg:linear', colsample_bytree = 0.3, learning_rate = 0.1,
                    max_depth = 5, alpha = 10, n_estimators = 10)
    model.fit(X_train, y_train)
    # make predictions for test data
    y_pred = model.predict(X_test)
    predictions = [round(value) for value in y_pred]
    
    # evaluate predictions
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print("RMSE: %f" % (rmse))
    st.write("RMSE: %f" % (rmse))
    
    # cv_results contains train and test RMSE metrics for each boosting round
    params = {"objective":"reg:linear",'colsample_bytree': 0.3,'learning_rate': 0.1,
                    'max_depth': 5, 'alpha': 10}
    
    cv_results = xgb.cv(dtrain=data_dmatrix, params=params, nfold=3,
                        num_boost_round=50,early_stopping_rounds=10,metrics="rmse", as_pandas=True, seed=123)
    
    print(cv_results.head())
    
    st.write(cv_results)
    
    
    #from xgboost import plot_importance
    
    
    #accuracy = accuracy_score(y_test, predictions)
    #print("Accuracy: %.2f%%" % (accuracy * 100.0))
    
    #Store final dataset into an excel
    #df.to_excel(r'C:\2021_NehalPersonal\Project\Decentraland_USDPrice.xlsx', sheet_name='Data', index = False)
