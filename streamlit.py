import streamlit as st


main_page = st.Page("Project_introduction.py", title="Project Introduction")
page_2 = st.Page("View_tables.py", title="View Tables")
page_3 = st.Page("crud.py", title="CRUD Operations")
page_4 = st.Page("sql_queries.py", title="SQL Queries")
page_5 = st.Page("Filter.py", title="Filter tables")
page_6 = st.Page("personal.py", title="Personal Details")
page_7 = st.Page("learner.py", title="Learner SQL Queries")
page_8 = st.Page("user.py", title="User Introduction")

pg = st.navigation([main_page, page_2, page_3,page_4,page_5,page_6,page_7,page_8])


pg.run()

