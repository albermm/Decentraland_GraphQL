# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt

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

    
    ## Dashboard formatting in Streamlit ##
    
    st.sidebar.title('Decentraland')
    
    st.header("Map - Parcel Sale Price")
    st.sidebar.header("Parameters for the Map")
    
    
    #Side slider bar
    x_range = st.sidebar.slider('X-Coordinate Range', value= [-200, 200])
    y_range = st.sidebar.slider('Y-Coordinate Range', value= [-200, 200])
    
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
                (df['transaction_date'] <= date_transaction)&
                (df['price_USD'] >= usd_range[0])&
                (df['price_USD'] <= usd_range[1])]
    
    
    #Plot Data in a Heatmap for Area Average Price
    c = alt.Chart(df_dashboard).mark_circle().encode(
        x='x', 
        y='y', 
        #size= 'area_avg_price',
        size = alt.Size('current_rate_pricemana', scale=alt.Scale(range=[25, 500])),
        color = alt.Color('current_rate_pricemana', scale=alt.Scale(scheme= 'plasma')),
        tooltip=['x', 'y', 'current_rate_pricemana']).properties(
        width=500,
        height=450).configure_mark(
        opacity= 1,
        color='red'
    ).interactive()
            
    st.altair_chart(c, use_container_width=True)
    
    #Store final dataset into an excel
    #df.to_excel(r'C:\2021_NehalPersonal\Project\Decentraland_USDPrice.xlsx', sheet_name='Data', index = False)
