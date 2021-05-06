# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 15:37:50 2020

@author: jsoares1
"""

import pandas as pd
import streamlit as st

#Import data from DB
sql1='SELECT PDETLH.schedule_number,PDETLH.start_date_time, PDETLH.schedule_type, PDETLH.job_key, PDETLH.program, PDETLH.scheduled_trim FROM PDETLH'
sql2='SELECT PDETLH.schedule_number,PDETLH.start_date_time, PDETLH.schedule_type, PDETLH.job_key, PDETLH.program, PDETLH.scheduled_trim FROM PDETLH'
sql3='SELECT PDETLH.schedule_number,PDETLH.start_date_time, PDETLH.schedule_type, PDETLH.job_key, PDETLH.program, PDETLH.scheduled_trim FROM PDETLH'
sql4='SELECT PHEADH.program, PHEADH.created_date_time, PHEADH.issued_date_time FROM PHEADH'
sql5='SELECT PHEADH.program, PHEADH.created_date_time, PHEADH.issued_date_time FROM PHEADH'
sql6='SELECT PHEADH.program, PHEADH.created_date_time, PHEADH.issued_date_time FROM PHEADH'

#Creating engine to query
from sqlalchemy import create_engine
engine1 = create_engine('mysql+pymysql://kiwireport:rigkiwi0215@lx38501000p.westrock.com/0005_map')
engine2 = create_engine('mysql+pymysql://kiwireport:rigkiwi0215@10.173.132.11/0004_map')
engine3 = create_engine('mysql+pymysql://kiwireport:rigkiwi0215@10.178.132.11/0003_map')

#Putting query on DataFrame and organize
FEPF_program =pd.read_sql_query(sql1, engine1)
FEB_program =pd.read_sql_query(sql2, engine2)
FEA_program =pd.read_sql_query(sql3, engine3)
FEPF_program.rename(columns={'start_date_time':'Corr_start'}, inplace=True)
FEB_program.rename(columns={'start_date_time':'Corr_start'}, inplace=True)
FEA_program.rename(columns={'start_date_time':'Corr_start'}, inplace=True)
FEPF_history=pd.read_sql_query(sql4, engine1)
FEB_history=pd.read_sql_query(sql5, engine2)
FEA_history=pd.read_sql_query(sql6, engine3)


#Applying data filter FEPF
from datetime import date

data1 = pd.Timestamp(date(2021,1,1))
data2 = pd.Timestamp(date(2021,5,31))

FEPF_program = FEPF_program[
    (FEPF_program['Corr_start']>data1) & 
    (FEPF_program['Corr_start']<data2)]

#Applying data filter FEB
FEB_program = FEB_program[
    (FEB_program['Corr_start']>data1) & 
    (FEB_program['Corr_start']<data2)]

#Applying data filter FEA
FEA_program = FEA_program[
    (FEA_program['Corr_start']>data1) & 
    (FEA_program['Corr_start']<data2)]

#Creating DataFrame to schedule type
Data = [['A', 'GRADE SCHEDULE'], ['B', 'MACHINE SCHEDULE'], ['D', 'REWORKED MACHINE SCH'],['M', 'MANUAL']]
Sch_Class=pd.DataFrame(Data, columns = ['schedule_type','Sch_Description'])

#Creating a merge with Dataframes to get sch type
FEPF_program = pd.merge(FEPF_program,Sch_Class[['schedule_type', 'Sch_Description']], how='left', left_on='schedule_type', right_on='schedule_type')
FEB_program = pd.merge(FEB_program,Sch_Class[['schedule_type', 'Sch_Description']], how='left', left_on='schedule_type', right_on='schedule_type')
FEA_program = pd.merge(FEA_program,Sch_Class[['schedule_type', 'Sch_Description']], how='left', left_on='schedule_type', right_on='schedule_type')

#Creating a merge with Dataframes to get program details
FEPF_program = pd.merge(FEPF_program,FEPF_history[['program', 'created_date_time','issued_date_time']], how='left', left_on='program', right_on='program')
FEB_program = pd.merge(FEB_program,FEB_history[['program', 'created_date_time','issued_date_time']], how='left', left_on='program', right_on='program')
FEA_program = pd.merge(FEA_program,FEA_history[['program', 'created_date_time','issued_date_time']], how='left', left_on='program', right_on='program')

#creating month split
FEPF_program['Month']=FEPF_program['Corr_start'].dt.month_name()
FEB_program['Month']=FEB_program['Corr_start'].dt.month_name()
FEA_program['Month']=FEA_program['Corr_start'].dt.month_name()

#Creating column plant name
PF_name='FEPF'
Blu_name='FEB'
Aru_name='FEA'

FEPF_program['Plant']=PF_name
FEB_program['Plant']=Blu_name
FEA_program['Plant']=Aru_name

#Move to Dataframe to get series analysis
FEPF_Time=FEPF_program
FEPF_Time=FEPF_Time.sort_values(['created_date_time']).drop_duplicates(['program'], keep='first')
FEPF_Time['Time_analysis']=FEPF_Time['created_date_time'].diff(1)
FEB_Time=FEB_program
FEB_Time=FEB_Time.sort_values(['created_date_time']).drop_duplicates(['program'], keep='first')
FEB_Time['Time_analysis']=FEB_Time['created_date_time'].diff(1)
FEA_Time=FEA_program
FEA_Time=FEA_Time.sort_values(['created_date_time']).drop_duplicates(['program'], keep='first')
FEA_Time['Time_analysis']=FEA_Time['created_date_time'].diff(1)

#Consolidating Dataframes
Intermediate_program_base=[FEPF_program,FEB_program,FEA_program]
General_program_BU=pd.concat(Intermediate_program_base)

Intermediate_normalized=[FEPF_Time, FEB_Time, FEA_Time]
General_program=pd.concat(Intermediate_normalized)

#Export DataFrame to excel
wfile = 'General_program.xlsx'
General_program.to_excel(wfile, 'sheet1', index=False)


#Setting dataset for analysis purpose
FEA_summary=FEA_program.groupby('Month').aggregate({'schedule_number': 'count'})

st.line_chart(FEA_summary)

#Export DataFrame to excel
#wfile = 'FEPF_Time.xlsx'
#FEPF_Time.to_excel(wfile, 'sheet1', index=False)

#Export DataFrame to excel
#wfile = 'FEB_Time.xlsx'
#FEB_Time.to_excel(wfile, 'sheet1', index=False)

#Export DataFrame to excel
#wfile = 'FEA_Time.xlsx'
#FEA_Time.to_excel(wfile, 'sheet1', index=False)





