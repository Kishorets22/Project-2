import streamlit as st

st.set_page_config(page_title="User Introduction", layout="centered")

st.title("User Introduction")

st.markdown("""
Welcome! This page gives a short introduction about the user.

Edit the placeholders below with your real information.
""")

st.subheader("Hello — I'm Kishore T S")
st.write("A brief one-line introduction goes here (e.g. 'Data enthusiast focusing on analytics and visualization').")

st.subheader("About me")
st.markdown("""
- Background in machine learning and data engineering with hands-on experience building and deploying models.
- Strong Python skills (pandas, NumPy) and experience with deep learning frameworks (PyTorch, TensorFlow).
- Experienced in feature engineering, model evaluation, and productionizing ML workflows (ML pipelines, monitoring).
- Passionate about building reliable, interpretable, and scalable AI systems that deliver business value.
""")

st.subheader("Current goals")
st.markdown("""
- Build production-grade ML pipelines and automate training/deployment (CI/CD for models).
- Deploy and monitor models in production (containerization, orchestration, A/B testing, observability).
- Improve model performance and interpretability; adopt best practices for data quality and validation.
- Prototype LLM / transformer applications and integrate them into product workflows.
- Expand skills in MLOps tools (MLflow, DVC), cloud deployment (AWS/GCP) and scalable serving.
""")


