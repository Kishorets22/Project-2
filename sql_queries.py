import streamlit as st
import pandas as pd

st.set_page_config(page_title="Provider Queries", layout="wide")
st.title("Provider / Food / Claims/ Receivers - Queries")

# Load datasets (CSV files included in the repository)
@st.cache_data
def load_data():
	providers = pd.read_csv("providers_data.csv")
	receivers = pd.read_csv("receivers_data.csv")
	food = pd.read_csv("food_listings_data.csv")
	claims = pd.read_csv("claims_data.csv")
	return providers, receivers, food, claims

providers, receivers, food, claims = load_data()

st.sidebar.header("SQL Queries")
questions = [
	"Which type of food provider contributes the most food?",
	"Contact information of food providers in a specific city",
	"How many food providers and receivers are there in each city?",
	"Which receivers have claimed the most food?",
	"Which city has the highest number of food listings?",
	"What are the most commonly available food types?",
	"What is the total quantity of food available from all providers?",
	"How many food claims have been made for each food item? (Completed)",
	"Which receiver has had the highest number of successful food claims?",
	" Percentage of food claims completed vs pending vs canceled",
	"Which meal type is claimed the most?",
	"What is the total quantity of food donated by each provider?",
	"What is the average quantity of food claimed per receiver?",
	# keep previous extra options available below
	"Show raw tables",
]

choice = st.sidebar.selectbox("Select question", questions)
top_n = st.sidebar.slider("Rows to show (top n)", min_value=5, max_value=200, value=20)


def show_df(title, df):
	st.subheader(title)
	st.dataframe(df.head(top_n), use_container_width=True)


if choice == "Which type of food provider contributes the most food?":
	# Sum of Quantity by Provider_Type
	df = food.groupby('Provider_Type', dropna=False)['Quantity'].sum().reset_index().rename(columns={'Quantity':'Total_Quantity'}).sort_values('Total_Quantity', ascending=False)
	show_df("Total quantity contributed by Provider_Type", df)

elif choice == "Contact information of food providers in a specific city":
	cities = sorted(providers['City'].dropna().unique().tolist())
	sel_city = st.sidebar.selectbox("Select city", options=["<all>"] + cities)
	if sel_city == "<all>":
		df = providers[['Provider_ID','Name','Type','City','Contact']]
	else:
		df = providers[providers['City'].str.contains(sel_city, case=False, na=False)][['Provider_ID','Name','Type','City','Contact']]
	show_df(f"Providers contact in {sel_city}", df)

elif choice == "How many food providers and receivers are there in each city?":
	prov = providers.groupby('City', dropna=False)['Provider_ID'].nunique().reset_index().rename(columns={'Provider_ID':'total_providers'})
	recv = receivers.groupby('City', dropna=False)['Receiver_ID'].nunique().reset_index().rename(columns={'Receiver_ID':'total_receivers'})
	combined = pd.merge(prov, recv, on='City', how='outer').fillna(0)
	combined['total_providers'] = combined['total_providers'].astype(int)
	combined['total_receivers'] = combined['total_receivers'].astype(int)
	combined = combined.sort_values(['total_providers','total_receivers'], ascending=False)
	show_df("Providers and Receivers by City", combined)

elif choice == "Which receivers have claimed the most food?":
	df = claims.groupby('Receiver_ID').size().reset_index(name='Total_Claims').sort_values('Total_Claims', ascending=False)
	df = df.merge(receivers, on='Receiver_ID', how='left')
	show_df("Receivers by total claims", df[['Receiver_ID','Name','Type','Total_Claims']])

elif choice == "Which city has the highest number of food listings?":
	df = food.groupby('Location', dropna=False).size().reset_index(name='count').sort_values('count', ascending=False)
	show_df("Food listings by Location", df)

elif choice == "What are the most commonly available food types?":
	df = food.groupby('Food_Name', dropna=False).size().reset_index(name='count').sort_values('count', ascending=False)
	show_df("Food_Name counts", df)

elif choice == "What is the total quantity of food available from all providers?":
	total_qty = int(food['Quantity'].sum())
	st.subheader("Total quantity of food available from all providers")
	st.metric("Total Quantity", total_qty)

elif choice == "How many food claims have been made for each food item? (Completed)":
	completed = claims[claims['Status'].str.lower()=='completed']
	merged = completed.merge(food, on='Food_ID', how='left')
	df = merged.groupby('Food_Name').size().reset_index(name='Total_Claims').sort_values('Total_Claims', ascending=False)
	show_df("Completed claims per Food Item", df)

elif choice == "Which receiver has had the highest number of successful food claims?":
	completed = claims[claims['Status'].str.lower() == 'completed']
	agg = completed.groupby('Receiver_ID').size().reset_index(name='Total_Claims').sort_values('Total_Claims', ascending=False)
	agg = agg.merge(receivers, left_on='Receiver_ID', right_on='Receiver_ID', how='left')
	show_df("Top receivers by completed claims", agg[['Receiver_ID','Name','Type','Total_Claims']])

elif choice == "Percentage of food claims completed vs pending vs canceled":
	status_counts = claims['Status'].value_counts(dropna=False).rename_axis('Status').reset_index(name='Count')
	status_counts['Percentage'] = (status_counts['Count'] / status_counts['Count'].sum() * 100).round(2)
	show_df("Claims status breakdown", status_counts)

elif choice == "Which meal type is claimed the most?":
	merged = claims.merge(food, on='Food_ID', how='left')
	completed = merged[merged['Status'].str.lower() == 'completed']
	df = completed.groupby('Meal_Type').size().reset_index(name='Total').sort_values('Total', ascending=False)
	show_df("Meal_Type counts for completed claims", df)

elif choice == "What is the total quantity of food donated by each provider?":
	df = food.groupby('Provider_ID', dropna=False)['Quantity'].sum().reset_index().rename(columns={'Quantity':'Total_Quantity'}).sort_values('Total_Quantity', ascending=False)
	show_df("Total Quantity by Provider", df)

elif choice == "What is the average quantity of food claimed per receiver?":
	merged = claims.merge(food, on='Food_ID', how='left')
	df = merged.groupby('Receiver_ID')['Quantity'].mean().reset_index().rename(columns={'Quantity':'Average_Quantity'}).sort_values('Average_Quantity', ascending=False)
	show_df("Average claimed quantity per Receiver", df)

