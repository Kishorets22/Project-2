import streamlit as st

st.set_page_config(page_title="Personal Info", layout="centered")

st.title("Personal Information")

with st.container():
	st.subheader("Name")
	st.write("Kishore T S")

	st.subheader("Role")
	st.write("AI Engineer")

	st.subheader("Contact")
	st.write("Email: email@example.com")
	st.write("Phone: +1 234 567 890")

	st.subheader("Short Bio")
	st.write("Experienced data analyst with a background in Python, pandas, SQL and Streamlit. I build data pipelines, create dashboards and help teams turn raw data into actionable insights.")

	st.subheader("Skills")
	st.write("Python, pandas, SQL, Streamlit, data visualization, data cleaning, ETL")

	