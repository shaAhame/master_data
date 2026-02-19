import streamlit as st
import pandas as pd

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Customer Sales Dashboard",
    layout="wide"
)
st.title("📊 Customer Sales Dashboard")

# -----------------------------
# Load Data
# -----------------------------
try:
    master_df = pd.read_csv("data/master_db.csv")
except FileNotFoundError:
    st.error("Master CSV not found! Make sure 'data/master_db.csv' exists.")
    st.stop()

# Clean column names (remove leading/trailing spaces)
master_df.columns = master_df.columns.str.strip()

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Filters")

# Branch filter
branch_options = ["All"] + master_df["Branch"].dropna().unique().tolist()
selected_branch = st.sidebar.selectbox("Select Branch:", branch_options)

filtered_df = master_df if selected_branch == "All" else master_df[master_df["Branch"] == selected_branch]

# Date filter
if "Date" in filtered_df.columns:
    date_options = ["All"] + sorted(filtered_df["Date"].dropna().unique().tolist())
    selected_date = st.sidebar.selectbox("Select Date:", date_options)
    if selected_date != "All":
        filtered_df = filtered_df[filtered_df["Date"] == selected_date]

# IMEI search
if "IMEI" in filtered_df.columns:
    imei_search = st.sidebar.text_input("Search IMEI:")
    if imei_search:
        filtered_df = filtered_df[filtered_df["IMEI"].astype(str).str.contains(imei_search, case=False, na=False)]

# -----------------------------
# Display Table
# -----------------------------
st.subheader("Filtered Data")

# Highlight max sales if column exists
highlight_column = "Sales Amount"
if highlight_column in filtered_df.columns:
    st.dataframe(filtered_df.style.highlight_max(subset=[highlight_column], color="lightgreen"))
else:
    st.dataframe(filtered_df)

# -----------------------------
# Summary Metrics
# -----------------------------
st.markdown("### Summary Metrics")
col1, col2, col3 = st.columns(3)

col1.metric("Total Customers", filtered_df["Customer Name"].nunique() if "Customer Name" in filtered_df.columns else 0)
col2.metric("Total Sales", filtered_df.shape[0])
col3.metric("Unique IMEIs", filtered_df["IMEI"].nunique() if "IMEI" in filtered_df.columns else 0)

# -----------------------------
# Download CSV
# -----------------------------
st.markdown("### Download Data")
st.download_button(
    label="Download Filtered CSV",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name="customer_master_filtered.csv",
    mime="text/csv"
)
