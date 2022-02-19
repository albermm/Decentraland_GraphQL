# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 21:11:15 2022

@author: Nehal
"""
import os
import streamlit as st

#Custom Imports
from multipage import MultiPage
from pages import ShowDataApp, DecentralandDraftApp, Decentraland_ParcelSalePriceApp
#from pages import DecentralandDraft, Decentraland_ParcelSalePrice,XGBoost_Decentraland,WebAppPage2

# Create an instance of the app 
app = MultiPage()

# Title of the main page

#col2.title("Data Storyteller Application")

# Add all your application here
app.add_page("Map- Area Average Price", DecentralandDraftApp.app)
app.add_page("Map- Parcel Sale Price", Decentraland_ParcelSalePriceApp.app)
app.add_page("Show Data", ShowDataApp.app)
#app.add_page("XG Boost", XGBoost_DecentralandApp.app)

# The main app
app.run()