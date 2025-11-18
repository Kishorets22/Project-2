import streamlit as st
import mysql.connector
import pandas as pd
st.title("View Tables")
table = st.selectbox('Select Table', ['Providers','recievers','FoodListing','Claims'])
con= mysql.connector.connect(
        host="localhost",         
        user="root",             
        password="root",   
        database="project"   
    )
if table:
    try:
        query ="Select * from"+" "+table
        df=pd.read_sql(query,con)
        st.dataframe(df)

        
    except Exception as e:
        st.error("Error Loading table:"+str(e))