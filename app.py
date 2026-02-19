import streamlit as st
import pandas as pd

# ------------------------------
# Page Config
# ------------------------------
st.set_page_config(
    page_title="Customer Sales Dashboard",
    layout="wide",
    page_icon="📊"
)

# ------------------------------
# Title
# ------------------------------
st.title("📊 Customer Sales Dashboard")
st.markdown("Analyze branch-wise sales, customers, and IMEI details easily.")

# ------------------------------
# Load Data
# ------------------------------
master_df = pd.read_csv("data/master_db.csv")

# ------------------------------
# Sidebar Filters
# ------------------------------
st.sidebar.header("🔍 Filters")

# Branch filter
branch_options = ["All"] + master_df["Branch"].sort_values().unique().tolist()
selected_branch = st.sidebar.selectbox("Select Branch:", branch_options)

# Filter by branch
filtered_df = master_df if selected_branch == "All" else master_df[master_df["Branch"] == selected_branch]

# Date filter
date_options = ["All"] + sorted(filtered_df["Date"].unique())
selected_date = st.sidebar.selectbox("Select Date:", date_options)

if selected_date != "All":
    filtered_df = filtered_df[filtered_df["Date"] == selected_date]

# Search by IMEI
imei_search = st.sidebar.text_input("Search by IMEI:")
if imei_search:
    filtered_df = filtered_df[filtered_df["IMEI"].astype(str).str.contains(imei_search)]

# ------------------------------
# Summary Metrics
# ------------------------------
st.markdown("### 📈 Summary Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Customers", filtered_df["Customer Name"].nunique(), "👤")
col2.metric("Total Sales", filtered_df["Item"].count(), "🛒")
col3.metric("Unique IMEIs", filtered_df["IMEI"].nunique(), "📱")

# ------------------------------
# Table Display
# ------------------------------
st.markdown("### 📋 Detailed Table")
st.dataframe(filtered_df.style.highlight_max(subset=["Sales Amount"], color="lightgreen"))

# ------------------------------
# Download CSV
# ------------------------------
st.markdown("### 💾 Download Data")
st.download_button(
    label="Download CSV",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='customer_master.csv',
    mime='text/csv'
)

# ------------------------------
# Footer
# ------------------------------
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")
