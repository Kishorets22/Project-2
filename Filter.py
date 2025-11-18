import streamlit as st
import mysql.connector
import pandas as pd

# connect to database
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="project"
    )

st.title("Table Filter")
tables = ["providers", "recievers", "foodlisting", "claims"]
selected_table = st.selectbox("Select a table", tables)
st.write("### Choose a filter")


if selected_table == "providers":
    Type = st.selectbox("Select Type of Provider", ['None','Supermarket','Grocery Store','Restaurant','Catering Service'])
    id = st.text_input("Enter provider id")
    city = st.text_input("Enter city")

    conditions = []
    if Type and Type != "None":
        conditions.append(f"Type LIKE '%{Type}%'")
    if id:
        conditions.append(f"id LIKE '%{id}%'")
    if city:
        conditions.append(f"city LIKE '%{city}%'")

    query = "SELECT * FROM providers"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)



elif selected_table == "recievers":
     Type = st.selectbox("Select Type of receiver", ['None','NGO','Individual','Shelter'])
     id = st.text_input("Enter receiver id")
     city = st.text_input("Enter city")

     conditions = []
     if Type and Type != "None":
         conditions.append(f"Type LIKE '%{Type}%'")
     if id:
         conditions.append(f"Receiver_ID LIKE '%{id}%'")
     if city:
         conditions.append(f"city LIKE '%{city}%'")

     query = "SELECT * FROM recievers"
     if conditions:
         query += " WHERE " + " AND ".join(conditions)


elif selected_table == "foodlisting":
    Food_Type = st.selectbox("Select Food Type", ['None','Perishable','Non-perishable','Prepared'])
    Meal_Type = st.selectbox("Select Meal Type", ['None','Breakfast','Lunch','Dinner','Snack'])
    food_id = st.text_input("Enter Food ID")
    food_name = st.text_input("Enter Food Name")
    provider_id = st.text_input("Enter Provider ID")
    location = st.text_input("Enter Location")
    expiry = st.text_input("Enter Expiry Date (YYYY-MM-DD or partial)")

    conditions = []
    if Food_Type and Food_Type != 'None':
        conditions.append(f"Food_Type LIKE '%{Food_Type}%'")
    if Meal_Type and Meal_Type != 'None':
        conditions.append(f"Meal_Type LIKE '%{Meal_Type}%'")
    if food_name:
        conditions.append(f"Food_Name LIKE '%{food_name}%'")
    if provider_id:
        conditions.append(f"Provider_ID LIKE '%{provider_id}%'")
    if location:
        conditions.append(f"Location LIKE '%{location}%'")
    if expiry:
        conditions.append(f"Expiry_Date LIKE '%{expiry}%'")

    query = "SELECT * FROM foodlisting"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)


elif selected_table == "claims":
    status = st.selectbox("Select Claim Status", ['None','Pending','Cancelled','Completed'])
    claim_id = st.text_input("Enter Claim ID")
    timestamp = st.text_input("Enter Timestamp (YYYY-MM-DD or partial)")

    conditions = []
    if status and status != 'None':
        conditions.append(f"Status LIKE '%{status}%'")
    if claim_id:
        conditions.append(f"Claim_ID LIKE '%{claim_id}%'")
    if timestamp:
        conditions.append(f"Timestamp LIKE '%{timestamp}%'")

    query = "SELECT * FROM claims"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

 



if st.button("Show Data"):
    try:
        conn = get_connection()
        df = pd.read_sql(query, conn)
        st.dataframe(df,use_container_width=True, height=500)
        conn.close()
    except Exception as e:
        st.error("Error loading data: " + str(e))