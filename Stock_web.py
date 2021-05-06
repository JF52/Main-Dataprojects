# -*- coding: utf-8 -*-
"""
Created on Thu May  6 15:18:33 2021

@author: jsoares1
"""

import pandas as pd
import streamlit as st

#import original dataset from excel - Stock last quarter
Stock_quarter=pd.read_excel("Stock_quarter.xlsx")

#Creating web visualization
st.title("Blumenau - The Stock Analysis Graph")
st.markdown('The Dashboard will evaluate the composition of stock in between January-21 and March-21')

#Setting dataset for analysis purpose
Stock_summary_1=Stock_quarter.groupby('Month').aggregate({'M²_total': 'sum'})

Stock_summary_2=Stock_quarter.groupby('Month').aggregate({'jobnumber': 'count'})

st.line_chart(Stock_summary_1)

st.bar_chart(Stock_summary_2)