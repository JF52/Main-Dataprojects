# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 10:11:13 2021

@author: jsoares1
"""

import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

#import original dataset from excel - Stock last quarter
Stock_quarter=pd.read_excel("General_stock_analysis.xlsx")

#Creating engine to DB connection
from sqlalchemy import create_engine
engine1 = create_engine('mssql+pyodbc://espreport:espreportPW1@KiwiESP')

#Import Orders from ESP
sql1='SELECT espOrder.jobnumber, espOrder.duedaterisk, espOrder.entrydate, espOrder.priority, espOrder.orderedquantity, espOrder.producedquantity, espOrder.creditoverridedate, espOrder.length, espOrder.width, espOrder.originalduedate, espOrder.totalarea, espOrder.targetquantity, espOrder.orderstatus, espOrder.jobtype, espOrder.duedate, espOrder.designnumber, espOrder.ordertype, orgPlant.name, orgCompany.name AS Custname FROM espOrder  INNER JOIN orgPlant ON espOrder.owningplantID = orgPlant.ID INNER JOIN OrgCompany  ON espOrder.companyID = orgCompany.ID WHERE orgPlant.plantcode = 0004'
General_orders=pd.read_sql_query(sql1, engine1)
General_orders.rename(columns={'entrydate':'Data'}, inplace=True)

#Applying data filter 
from datetime import date

data1 = pd.Timestamp(date(2019,1,1)) #before 2020,12,1
data2 = pd.Timestamp(date(2021,4,30)) #before 2021,4,30

General_orders = General_orders[
    (General_orders['Data']>data1) & 
    (General_orders['Data']<data2)]

#Creating and applying function to get ordertyoe description
def ordclass(x):
    if x == 1:
        Class = 'Calloff'
        return Class
    if x == 2:
        Class = 'Topup'
        return Class
    else:
        Class = 'Normal'
        return Class
    
General_orders['Ordertype_desc']=np.vectorize(ordclass)(General_orders['ordertype'])

#Drop cancelled orders
General_orders.drop(General_orders.loc[General_orders['Ordertype_desc']=='Calloff'].index, inplace=True)

#Casting variables to get the right format
General_orders['jobnumber']=General_orders['jobnumber'].astype(int)
Stock_quarter['jobnumber']=Stock_quarter['jobnumber'].astype(int)

#Merging to get duedate to stock file and order type
Stock_quarter = pd.merge(Stock_quarter,General_orders[['jobnumber', 'duedate',]], how='left', left_on='jobnumber', right_on='jobnumber')
Stock_quarter = pd.merge(Stock_quarter,General_orders[['jobnumber', 'Ordertype_desc',]], how='left', left_on='jobnumber', right_on='jobnumber')

#Import data set from MAP to evaluate 9991 feedback
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://kiwireport:rigkiwi0215@10.173.132.11/0004_map')
sql2='SELECT FACTRY.job_number, FACTRY.spec_number, FACTRY.finish_datetime, FACTRY.quantity_good_out, FACTRY.exit_length, FACTRY.exit_width, FACTRY.customer_name FROM FACTRY WHERE FACTRY.machine_number = 9991 OR FACTRY.machine_number = 7998 AND FACTRY.finish_datetime BETWEEN "2019-01-01 00:00:00.000" AND "2021-12-31 23:59:59.000"'
End_production =pd.read_sql_query(sql2, engine)
End_production.rename(columns={'finish_datetime':'Data_feedback'}, inplace=True)
End_production.rename(columns={'job_number':'jobnumber'}, inplace=True)

#To keep the first feedback
End_production=End_production.drop_duplicates(subset=['jobnumber'], keep="first")

#Casting variables to get the right format
End_production['jobnumber']=End_production['jobnumber'].astype(int)

#Merging to get feedback date to stock file
Stock_quarter = pd.merge(Stock_quarter,End_production[['jobnumber', 'Data_feedback',]], how='left', left_on='jobnumber', right_on='jobnumber')

#treating job transfer cases - not in focus
Stock_quarter['Data_feedback']=Stock_quarter['Data_feedback'].fillna('transfer')
Stock_quarter.drop(Stock_quarter.loc[Stock_quarter['Data_feedback']=='transfer'].index, inplace=True)

#casting to get properly format
Stock_quarter['Data_feedback']=pd.to_datetime(Stock_quarter['Data_feedback'])

#Get delta between duedate and feedback date - stock basis
Stock_quarter['Delta_days']=Stock_quarter['duedate']-Stock_quarter['Data_feedback']
Stock_quarter['Delta_days']=Stock_quarter['Delta_days'].dt.days

def delta_class(x):
    if x>=0 and x<=1:
        Class='0.Na data'
        return Class
    if x>1 and x<=3:
        Class='1.Adiantado de 2 a 3 dias'
        return Class
    if x>3 and x <=7:
        Class='2.Adiantado de 4 a 7 dias'
        return Class
    if x>7:
        Class='3.Adiantado maior que 7 dias'
        return Class
    else:
        Class='4.Produzido com atraso'
        return Class

Stock_quarter['Delta_class']=np.vectorize(delta_class)(Stock_quarter['Delta_days'])

def findahead(x):
    if "Adiantado" in x:
        Class = '1.Adiantado'
        return Class
    if "Na data" in x:
        Class = '0.Na data'
        return Class
    else:
        Class = '2.Atrasado'
        return Class
    
Stock_quarter['General_class']=np.vectorize(findahead)(Stock_quarter['Delta_class'])

#Creating web visualization
st.title("Blumenau - The Stock Analysis Graph")
st.markdown('The Dashboard will evaluate the composition of stock in between January-21 and March-21')

#Setting dataset for analysis purpose
Stock_summary_1=Stock_quarter.groupby('Month').aggregate({'M²_total': 'sum'})

Stock_summary_2=Stock_quarter.groupby('Month').aggregate({'jobnumber': 'count'})

st.line_chart(Stock_summary_1)

st.bar_chart(Stock_summary_2)

#Export DataFrame to excel
#wfile = 'Stock_quarter.xlsx'
#Stock_quarter.to_excel(wfile, 'sheet1', index=False)

