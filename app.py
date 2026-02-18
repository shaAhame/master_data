import streamlit as st
import pandas as pd

st.set_page_config(page_title="Customer Sales Dashboard", layout="wide")
st.title("📊 Customer Sales Dashboard")

# Load master CSV
master_df = pd.read_csv("data/master_db.csv")

# Branch filter
branch_options = ["All"] + master_df["Branch"].unique().tolist()
selected_branch = st.selectbox("Select Branch:", branch_options)

filtered_df = master_df if selected_branch == "All" else master_df[master_df["Branch"] == selected_branch]

# Date filter
dates = ["All"] + sorted(filtered_df["Date"].unique().tolist())
selected_date = st.selectbox("Select Date:", dates)

if selected_date != "All":
    filtered_df = filtered_df[filtered_df["Date"] == selected_date]

# Display table
st.dataframe(filtered_df)

# Summary metrics
st.markdown("### Summary Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Customers", filtered_df["Customer Name"].nunique())
col2.metric("Total Sales", filtered_df["Item"].count())
col3.metric("Unique IMEIs", filtered_df["IMEI"].nunique())

# Download CSV
st.download_button(
    label="Download CSV",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='customer_master.csv',
    mime='text/csv'
)
