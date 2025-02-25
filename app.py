import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def process_order_report():
    st.markdown("<h1 style='text-align: center; color: #4A90E2;'>📊 Amazon Order Report Dashboard</h1>", unsafe_allow_html=True)
    uploaded_file = st.sidebar.file_uploader("Upload Amazon Order Report", type=["csv", "xlsx"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        required_columns = ["purchase-date", "order-status", "fulfillment-channel", "item-price", "ship-city", "sku", "product-name"]
        if any(col not in df.columns for col in required_columns):
            st.error("Missing required columns in uploaded file.")
            return
        df["purchase-date"] = pd.to_datetime(df["purchase-date"], errors='coerce').dt.tz_localize(None)
        order_status = st.sidebar.multiselect("Order Status", df["order-status"].dropna().unique(), default=df["order-status"].dropna().unique())
        fulfillment_channel = st.sidebar.multiselect("Fulfillment Channel", df["fulfillment-channel"].dropna().unique(), default=df["fulfillment-channel"].dropna().unique())
        min_date, max_date = df["purchase-date"].min().date(), df["purchase-date"].max().date()
        date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])
        filtered_df = df[(df["order-status"].isin(order_status)) & (df["fulfillment-channel"].isin(fulfillment_channel)) & (df["purchase-date"].between(pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])))]
        if filtered_df.empty:
            st.warning("No records found.")
            return
        total_orders, total_revenue, cancelled_orders = filtered_df.shape[0], filtered_df["item-price"].sum(), filtered_df[filtered_df["order-status"] == "Cancelled"].shape[0]
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Orders", total_orders)
        col2.metric("Total Revenue", f"Rs.{total_revenue:,.2f}")
        col3.metric("Cancelled Orders", cancelled_orders)
        fig = px.line(filtered_df.groupby(filtered_df["purchase-date"].dt.date).size().reset_index(name="Orders"), x="purchase-date", y="Orders", title="📈 Orders Over Time", markers=True)
        st.plotly_chart(fig, use_container_width=True)

def process_return_report():
    st.markdown("<h2 style='text-align: center; color: #E24A4A;'>🔄 Amazon Return Report Dashboard</h2>", unsafe_allow_html=True)
    uploaded_file = st.sidebar.file_uploader("Upload Amazon Return Report", type=["csv", "xlsx"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip().str.lower()
        numeric_columns = ["refunded amount", "order amount"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        selected_status = st.sidebar.multiselect("Return Request Status", options=df["return request status"].dropna().unique(), default=df["return request status"].dropna().unique())
        filtered_df = df[df["return request status"].isin(selected_status)]
        total_returns = filtered_df.shape[0]
        total_refunded_amount = filtered_df["refunded amount"].sum()
        col1, col2 = st.columns(2)
        col1.metric("Total Return Requests", total_returns)
        col2.metric("Total Refunded Amount", f"Rs.{total_refunded_amount:,.2f}")

def process_inventory():
    st.markdown("<h1>📊 Amazon Inventory Dashboard</h1>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("📂 Upload Inventory File", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        required_columns = ["sku", "asin", "price", "quantity"]
        if any(col not in df.columns for col in required_columns):
            st.error("Missing required columns.")
            return
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
        total_inventory, total_value, zero_inventory_skus = df["quantity"].sum(), (df["price"] * df["quantity"]).sum(), (df["quantity"] == 0).sum()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Inventory", f"{total_inventory:,}")
        col2.metric("Total Value", f"₹{total_value:,}")
        col3.metric("Zero Stock SKUs", f"{zero_inventory_skus:,}")
        stock_data = pd.DataFrame({"Stock Status": ["Zero Stock", "With Stock"], "Count": [zero_inventory_skus, df.shape[0] - zero_inventory_skus]})
        fig_pie = px.pie(stock_data, names="Stock Status", values="Count", title="📊 Stock Distribution", color_discrete_map={"Zero Stock": "red", "With Stock": "green"}, hole=0.3)
        st.plotly_chart(fig_pie, use_container_width=True)
        output_file = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Processed Inventory", output_file, "processed_inventory.csv", "text/csv")

st.sidebar.title("📌 Dashboard Menu")
menu = st.sidebar.radio("Select a Report:", ["Order Report", "Return Report", "Inventory Report"])
if menu == "Order Report":
    process_order_report()
elif menu == "Return Report":
    process_return_report()
elif menu == "Inventory Report":
    process_inventory()
st.sidebar.markdown("---")
st.sidebar.markdown("🚀 **Work done by Tech Assassins - Seller Rocket**")
