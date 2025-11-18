# import streamlit as st

# st.markdown("# Page 7 🎉")
# st.sidebar.markdown("# Page 7 🎉")
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Learner Queries", layout="wide")
st.title("Learner Queries")


@st.cache_data
def load_data():
	prov = pd.read_csv("providers_data.csv")
	recv = pd.read_csv("receivers_data.csv")
	food = pd.read_csv("food_listings_data.csv")
	claims = pd.read_csv("claims_data.csv")
	# ensure date parsing for convenience
	food['Expiry_Date'] = pd.to_datetime(food['Expiry_Date'], errors='coerce')
	claims['Timestamp'] = pd.to_datetime(claims['Timestamp'], errors='coerce')
	return prov, recv, food, claims

prov, recv, food, claims = load_data()

questions = [
	"Providers with highest average quantity per listing",
	"Providers with largest variety of food items (distinct Food_Name)",
	"Food items with lowest total stock",
	"Food listings expiring within the next N days",
	"Distribution of provider types across cities",
	"Claims status breakdown overall and by provider type",
	"Cancellation rate per provider",
	"Claims per day (time-series)",
	"Receivers that have never had a completed claim",
	"Top food items by average quantity per claim",
	"Providers with no claims",
	"Distribution: listings per provider (mean, median, percentiles)",
	"Top meal types by city"
]

st.sidebar.header("Learner Queries")
choice = st.sidebar.selectbox("Select question", questions)
# slicer: choose a start and end row to display
max_rows = max(200, len(prov), len(recv), len(food), len(claims))
row_slice = st.sidebar.slider("Rows to show (slice)", min_value=1, max_value=max_rows, value=(1, min(20, max_rows)), step=1)


def show_df(title, df):
	st.subheader(title)
	# apply the user-selected slice
	start, end = int(row_slice[0]), int(row_slice[1])
	if start < 1:
		start = 1
	if end < start:
		end = start
	# cap end to dataframe length
	end = min(end, len(df))
	st.dataframe(df.iloc[start-1:end], use_container_width=True)


if choice == questions[0]:

	df = food.groupby('Provider_ID', dropna=False)['Quantity'].mean().reset_index().rename(columns={'Quantity':'Avg_Quantity'}).sort_values('Avg_Quantity', ascending=False)
	show_df("Providers by average quantity per listing", df)

elif choice == questions[1]:

	df = food.groupby('Provider_ID')['Food_Name'].nunique().reset_index().rename(columns={'Food_Name':'Distinct_Food_Count'}).sort_values('Distinct_Food_Count', ascending=False)
	show_df("Providers by distinct food count", df)

elif choice == questions[2]:

	df = food.groupby('Food_Name')['Quantity'].sum().reset_index().rename(columns={'Quantity':'Total_Quantity'}).sort_values('Total_Quantity', ascending=True)
	show_df("Food items with lowest total stock", df)

elif choice == questions[3]:
	today = pd.Timestamp.today().normalize()
	df = food[(food['Expiry_Date'].notna()) & (food['Expiry_Date'] >= today)].sort_values('Expiry_Date')
	show_df("Food listings expiring from today onwards", df)

elif choice == questions[4]:
	df = prov.groupby(['City','Type']).size().reset_index(name='Count').sort_values(['City','Count'], ascending=[True,False])
	show_df("Provider types by city", df)

elif choice == questions[5]:
	overall = claims['Status'].value_counts(dropna=False).rename_axis('Status').reset_index(name='Count')
	overall['Percentage'] = (overall['Count'] / overall['Count'].sum() * 100).round(2)
	claims_food = claims.merge(food, on='Food_ID', how='left')
	by_provider_type = claims_food.groupby(['Provider_Type','Status']).size().reset_index(name='Count').sort_values(['Provider_Type','Count'], ascending=[True,False])
	st.subheader("Overall claims status breakdown")
	st.dataframe(overall, use_container_width=True)
	st.subheader("Claims status by provider type")
	start, end = int(row_slice[0]), int(row_slice[1])
	if start < 1:
		start = 1
	if end < start:
		end = start
	end = min(end, len(by_provider_type))
	st.dataframe(by_provider_type.iloc[start-1:end], use_container_width=True)

elif choice == questions[6]:
	claims_food = claims.merge(food, on='Food_ID', how='left')
	total_by_provider = claims_food.groupby('Provider_ID').size().reset_index(name='Total_Claims')
	cancelled_by_provider = claims_food[claims_food['Status'].str.lower()=='cancelled'].groupby('Provider_ID').size().reset_index(name='Cancelled')
	cancel_rate = total_by_provider.merge(cancelled_by_provider, on='Provider_ID', how='left').fillna(0)
	cancel_rate['Cancelled'] = cancel_rate['Cancelled'].astype(int)
	cancel_rate['Cancellation_Rate'] = (cancel_rate['Cancelled'] / cancel_rate['Total_Claims'] * 100).round(2)
	cancel_rate = cancel_rate.sort_values('Cancellation_Rate', ascending=False)
	show_df("Cancellation rate per provider", cancel_rate)

elif choice == questions[7]:
	df = claims.copy()
	df['Date'] = df['Timestamp'].dt.date
	ts = df.groupby('Date').size().reset_index(name='Count').sort_values('Date')
	show_df("Claims per day", ts)

elif choice == questions[8]:
	completed_receivers = claims[claims['Status'].str.lower()=='completed']['Receiver_ID'].unique()
	df = recv[~recv['Receiver_ID'].isin(completed_receivers)].reset_index(drop=True)
	show_df("Receivers with no completed claims", df)

elif choice == questions[9]:
	claimed = claims.merge(food, on='Food_ID', how='left')
	df = claimed.groupby('Food_Name')['Quantity'].mean().reset_index().rename(columns={'Quantity':'Avg_Quantity'}).sort_values('Avg_Quantity', ascending=False)
	show_df("Top food items by avg quantity per claim", df)

elif choice == questions[10]:
	claimed_food_ids = claims['Food_ID'].unique()
	providers_with_claims = food[food['Food_ID'].isin(claimed_food_ids)]['Provider_ID'].unique()
	df = prov[~prov['Provider_ID'].isin(providers_with_claims)].reset_index(drop=True)
	show_df("Providers with no claims", df)

elif choice == questions[11]:
	listings_count = food.groupby('Provider_ID').size().reset_index(name='Listings')
	stats = listings_count['Listings'].describe(percentiles=[0.25,0.5,0.75,0.9]).to_frame().T
	st.subheader("Listings per provider - summary stats")
	st.dataframe(stats, use_container_width=True)
	st.subheader("Top providers by listings")
	start, end = int(row_slice[0]), int(row_slice[1])
	if start < 1:
		start = 1
	if end < start:
		end = start
	top_provs = listings_count.sort_values('Listings', ascending=False)
	end = min(end, len(top_provs))
	st.dataframe(top_provs.iloc[start-1:end], use_container_width=True)

elif choice == questions[12]:
	meal_by_city = food.groupby(['Location','Meal_Type']).size().reset_index(name='Count').sort_values(['Location','Count'], ascending=[True,False])
	top_meal_by_city = meal_by_city.groupby('Location').head(1).reset_index(drop=True)
	show_df("Top Meal_Type by Location", top_meal_by_city)

