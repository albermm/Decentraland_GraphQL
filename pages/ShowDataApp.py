# -*- coding: utf-8 -*-
"""
Created on Sat Feb 19 21:06:01 2022

@author: Nehal
"""

import streamlit as st
import pandas as pd

def app():
    # @cache
    @st.cache
    def load_data():
        #datacsv = pd.read_csv("C:/Users/Nehal/JupyterNotebooks/TheGraph_Decentraland.csv") #To load it from local
        datacsv = pd.read_csv("TheGraph_Decentraland.csv") #To load it from Github
        df = pd.DataFrame(datacsv)
        return df

    df = load_data()

    df = df.rename(columns={'price_MANA': 'current_rate_pricemana'})

    # only keep relevant columns
    df = df [['x','y', 'date', 'current_rate_pricemana','price_USD', 'createdAt']]

    # Create date field
    df['transaction_date'] = pd.to_datetime(df['date']).dt.date
    df['transaction_date_created'] = pd.to_datetime(df['createdAt']).dt.date

    #### Calculate average price for a given area #### 
    # first add columns for ranges for average
    df['x_range_min'] = df["x"] - 20 
    df['x_range_max'] = df["x"] + 20 
    df['y_range_min'] = df["y"] - 20 
    df['y_range_max'] = df["y"] + 20 
    
    #Drop Duplicates
    df = df.drop_duplicates()

    # Create function that calculates the average price
    def area_avg_price_fun_eth(x_range_min, x_range_max, y_range_min, y_range_max):
        df_temp = df.loc[(df['x'] >= x_range_min) & (df['x'] <= x_range_max) & (df['y'] >= y_range_min) & (df['y'] <= y_range_max)]
        area_avg_price = df_temp['current_rate_pricemana'].mean()
        return area_avg_price

    df['area_avg_price'] = list(map(area_avg_price_fun_eth,df['x_range_min'],df['x_range_max'],df['y_range_min'],df['y_range_max']))

    
    st.title('Dataset')

    st.write('This is the dataframe used in this multi-page Decentraland app.')

    st.dataframe(df)