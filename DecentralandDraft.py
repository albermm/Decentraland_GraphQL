# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt


# =============================================================================
# Trial -- Using Rpy2 
# import plotly.express as px
# from statistics import mean
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

# @cache
@st.cache
def load_data():
    datacsv = pd.read_csv("C:/Users/Nehal/JupyterNotebooks/decentraland.csv")
    df = pd.DataFrame(datacsv)
    return df

df = load_data()

# only keep relevant columns
df = df [['x','y', 'last_sale_timestamp', 'current_rate_pricemana',
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
st.header("Map - Area Average Price")
st.sidebar.header("Decentraland")


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
            (df['transaction_date'] <= date_transaction)]


#Plot Data in a Heatmap for Area Average Price
c = alt.Chart(df_dashboard).mark_circle().encode(
    x='x', 
    y='y', 
    #size= 'area_avg_price',
    size = alt.Size('area_avg_price', scale=alt.Scale(range=[25, 500])),
    color = alt.Color('area_avg_price', scale=alt.Scale(scheme= 'plasma')),
    tooltip=['x', 'y', 'area_avg_price']).properties(
    width=500,
    height=450).configure_mark(
    opacity= 1,
    color='red'
).interactive()
        
st.altair_chart(c, use_container_width=True)

#Store final dataset into an excel
#df.to_excel(r'C:\2021_NehalPersonal\Project\Decentraland_USDPrice.xlsx', sheet_name='Data', index = False)
