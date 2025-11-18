import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
from typing import Tuple, Optional

st.set_page_config(page_title="CRUD Operations", layout="wide")
st.title("CRUD - Operations")


@st.cache_data
def load_all() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
	prov = pd.read_csv("providers_data.csv")
	recv = pd.read_csv("receivers_data.csv")
	food = pd.read_csv("food_listings_data.csv")
	claims = pd.read_csv("claims_data.csv")
	# parse dates if present
	if 'Expiry_Date' in food.columns:
		food['Expiry_Date'] = pd.to_datetime(food['Expiry_Date'], errors='coerce')
	if 'Timestamp' in claims.columns:
		claims['Timestamp'] = pd.to_datetime(claims['Timestamp'], errors='coerce')
	return prov, recv, food, claims


prov_df, recv_df, food_df, claims_df = load_all()

CSV_MAP = {
	"Providers": (prov_df, "providers_data.csv", "Provider_ID"),
	"Receivers": (recv_df, "receivers_data.csv", "Receiver_ID"),
	"Food Listings": (food_df, "food_listings_data.csv", "Food_ID"),
	"Claims": (claims_df, "claims_data.csv", "Claim_ID"),
}


def get_sql_conn() -> Optional[mysql.connector.connection_cext.CMySQLConnection]:
	try:
		return mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
	except Error as e:
		st.error(f"DB connection error: {e}")
		return None


def exec_sql(conn: mysql.connector.connection_cext.CMySQLConnection, stmt: str, params: Optional[Tuple] = None) -> Tuple[bool, str]:
	try:
		cur = conn.cursor()
		cur.execute(stmt, params or ())
		conn.commit()
		cur.close()
		return True, "ok"
	except Exception as e:
		return False, str(e)


def _sanitize_value(v):
	if v is None:
		return None
	if isinstance(v, str):
		s = v.strip()
		if s == "":
			return None
		# try int
		try:
			return int(s)
		except Exception:
			pass
		try:
			return float(s)
		except Exception:
			return s
	return v



sync_sql = True

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "project"


st.sidebar.write("SQL table name mapping (edit if your DB differs)")
table_providers = st.sidebar.text_input("Providers table name", value="providers")
table_receivers = st.sidebar.text_input("Receivers table name", value="receivers")
table_food = st.sidebar.text_input("Food table name", value="foodlisting")
table_claims = st.sidebar.text_input("Claims table name", value="claims")

TABLE_NAME_MAP = {
	"Providers": table_providers,
	"Receivers": table_receivers,
	"Food Listings": table_food,
	"Claims": table_claims,
}

CSV_TO_DB_COLS = {
	"Providers": {
		"Provider_ID": "id",
		"Name": "name",
		"Type": "type",
		"Address": "address",
		"City": "city",
		"Contact": "contact",
	},
	"Receivers": {
		"Receiver_ID": "Receiver_ID",
		"Name": "name",
		"Type": "type",
		"City": "city",
		"Contact": "contact",
	},
	"Food Listings": {
		"Food_ID": "Food_ID",
		"Food_Name": "Food_Name",
		"Quantity": "Quantity",
		"Expiry_Date": "Expiry_Date",
		"Provider_ID": "Provider_ID",
		"Provider_Type": "Provider_Type",
		"Location": "Location",
		"Food_Type": "Food_Type",
		"Meal_Type": "Meal_Type",
	},
	"Claims": {
		"Claim_ID": "Claim_ID",
		"Food_ID": "Food_ID",
		"Receiver_ID": "Receiver_ID",
		"Status": "Status",
		"Timestamp": "Timestamp",
	},
}


st.sidebar.markdown("---")
tbl_choice = st.sidebar.selectbox("Select table to operate on:", list(CSV_MAP.keys()))

df, csv_path, id_col = CSV_MAP[tbl_choice]
st.subheader(f"Working on: {tbl_choice}")

st.dataframe(df, use_container_width=True)

op = st.radio("Operation", ["Read / Filter", "Create", "Update", "Delete", "Reload CSV"], horizontal=True)


if op == "Reload CSV":
	prov_df, recv_df, food_df, claims_df = load_all()
	CSV_MAP["Providers"] = (prov_df, "providers_data.csv", "Provider_ID")
	CSV_MAP["Receivers"] = (recv_df, "receivers_data.csv", "Receiver_ID")
	CSV_MAP["Food Listings"] = (food_df, "food_listings_data.csv", "Food_ID")
	CSV_MAP["Claims"] = (claims_df, "claims_data.csv", "Claim_ID")



if op == "Read / Filter":
	st.markdown("### Quick filters")
	cols = df.columns.tolist()
	chosen_col = st.selectbox("Filter column (optional)", [None] + cols)
	if chosen_col:
		unique_vals = df[chosen_col].dropna().astype(str).unique().tolist()
		sel = st.multiselect("Values to keep", unique_vals, default=unique_vals[:5])
		if sel:
			out = df[df[chosen_col].astype(str).isin(sel)]
		else:
			out = df
	else:
		out = df
	st.dataframe(out, use_container_width=True)


if op == "Create":
	st.markdown("### Create a new record")
	with st.form("create_form"):
		inputs = {}
		for col in df.columns:
			if col == id_col:
				try:
					suggested = str(int(pd.to_numeric(df[col], errors='coerce').dropna().max()) + 1)
				except Exception:
					suggested = ""
				inputs[col] = st.text_input(col, value=suggested)
			else:
				inputs[col] = st.text_input(col)
		submitted = st.form_submit_button("Add")
	if submitted:
		df2 = df.copy()
		df2 = pd.concat([df2, pd.DataFrame([inputs])], ignore_index=True)
		df2.to_csv(csv_path, index=False)
		st.success("Record appended to CSV")
		if sync_sql:
			conn = get_sql_conn()
			if conn:
				cols = list(inputs.keys())
				db_cols = [CSV_TO_DB_COLS.get(tbl_choice, {}).get(c, c) for c in cols]
				qcols = ", ".join([f"`{c}`" for c in db_cols])
				placeholders = ",".join(["%s"] * len(cols))
				qtable = f"`{TABLE_NAME_MAP[tbl_choice]}`"
				stmt = f"INSERT INTO {qtable} ({qcols}) VALUES ({placeholders})"
				params = tuple(_sanitize_value(inputs[c]) for c in cols)
				ok, msg = exec_sql(conn, stmt, params)
				conn.close()
				if ok:
					st.success("Inserted into SQL")
				else:
					st.error(f"SQL insert failed: {msg}")
					st.write("--- SQL diagnostics ---")
					st.code(stmt)
					st.write("params:", params)


if op == "Update":
	st.markdown("### Update an existing record")
	id_values = df[id_col].astype(str).tolist()
	selected_id = st.selectbox("Select primary key value to edit", id_values)
	if selected_id:
		row = df[df[id_col].astype(str) == str(selected_id)].iloc[0]
		with st.form("update_form"):
			edits = {}
			for col in df.columns:
				edits[col] = st.text_input(col, value=str(row[col]))
			submitted = st.form_submit_button("Apply")
		if submitted:
			df2 = df.copy()
			mask = df2[id_col].astype(str) == str(selected_id)
			for col, val in edits.items():
				df2.loc[mask, col] = val
			df2.to_csv(csv_path, index=False)
			st.success("CSV updated")
			if sync_sql:
				conn = get_sql_conn()
				if conn:
					set_cols = [c for c in edits.keys() if c != id_col]
					# map to DB column names
					db_set_cols = [CSV_TO_DB_COLS.get(tbl_choice, {}).get(c, c) for c in set_cols]
					qset = ", ".join([f"`{c}` = %s" for c in db_set_cols])
					qtable = f"`{TABLE_NAME_MAP[tbl_choice]}`"
					qid = f"`{CSV_TO_DB_COLS.get(tbl_choice, {}).get(id_col, id_col)}`"
					stmt = f"UPDATE {qtable} SET {qset} WHERE {qid} = %s"
					params = tuple(_sanitize_value(edits[c]) for c in set_cols) + (_sanitize_value(selected_id),)
					ok, msg = exec_sql(conn, stmt, params)
					conn.close()
					if ok:
						st.success("SQL updated")
					else:
						st.error(f"SQL update failed: {msg}")
						st.write("--- SQL diagnostics ---")
						st.code(stmt)
						st.write("params:", params)


if op == "Delete":
	st.markdown("### Delete records")
	choices = st.multiselect("Select primary key values to delete", df[id_col].astype(str).tolist())
	if st.button("Delete selected"):
		if choices:
			df2 = df[~df[id_col].astype(str).isin(choices)]
			df2.to_csv(csv_path, index=False)
			st.success(f"Deleted {len(choices)} rows from CSV")
			if sync_sql:
				conn = get_sql_conn()
				if conn:
					placeholders = ",".join(["%s"] * len(choices))
					qtable = f"`{TABLE_NAME_MAP[tbl_choice]}`"
					qid = f"`{CSV_TO_DB_COLS.get(tbl_choice, {}).get(id_col, id_col)}`"
					stmt = f"DELETE FROM {qtable} WHERE {qid} IN ({placeholders})"
					params = tuple(_sanitize_value(c) for c in choices)
					ok, msg = exec_sql(conn, stmt, params)
					conn.close()
					if ok:
						st.success("Deleted from SQL")
					else:
						st.error(f"SQL delete failed: {msg}")
						st.write("--- SQL diagnostics ---")
						st.code(stmt)
						st.write("params:", params)
		else:
			st.info("No rows selected")


