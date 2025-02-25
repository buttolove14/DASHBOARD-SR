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
        top_cities = filtered_df["ship-city"].value_counts().head(10).reset_index()
        top_cities.columns = ["City", "Orders"]
        fig = px.bar(top_cities, x="City", y="Orders", title="🌆 Top Shipping Cities", color="Orders", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
        repeated_products = filtered_df["product-name"].value_counts().reset_index()
        repeated_products.columns = ["Product Name", "Purchase Count"]
        st.markdown("### 🔥 Most Repeatedly Purchased Products")
        st.dataframe(repeated_products.head(10))
        top_skus = filtered_df["sku"].value_counts().reset_index()
        top_skus.columns = ["SKU", "Order Count"]
        st.markdown("### 🏆 Top Selling SKUs")
        st.dataframe(top_skus.head(10))

def process_inventory():
    """Handles the UI and processing of inventory reports in Streamlit."""
    st.markdown("<h1>📊Amazon Inventory Dashboard</h1>", unsafe_allow_html=True)
    st.write("Upload your Excel file to generate insights on inventory.")
    uploaded_file = st.file_uploader("📂 Choose an Excel file", type=["xlsx"])
    if uploaded_file is not None:
        df = process_inventory_file(uploaded_file)
        if df is not None:
            st.markdown("### 📝 Processed Inventory Report")
            st.dataframe(df, height=600, use_container_width=True)
            total_inventory = int(df["quantity"].sum())
            total_value = int((df["price"] * df["quantity"]).sum())
            avg_price = round(df["price"].mean(), 2)
            zero_inventory_skus = int((df["quantity"] == 0).sum())
            available_skus = int((df["quantity"] > 0).sum())
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("📦 Total Inventory", f"{total_inventory:,}")
            col2.metric("💰 Total Value", f"₹{total_value:,}")
            col3.metric("📊 Avg. Price", f"₹{avg_price:,.2f}")
            col4.metric("🚫 Zero Stock SKUs", f"{zero_inventory_skus:,}")
            col5.metric("✅ Available SKUs", f"{available_skus:,}")
            stock_data = pd.DataFrame({"Stock Status": ["Zero Stock", "With Stock"], "Count": [zero_inventory_skus, available_skus]})
            if zero_inventory_skus > 0 or available_skus > 0:
                fig_pie = px.pie(stock_data, names="Stock Status", values="Count", title="📊 Zero Stock vs With Stock Distribution", color="Stock Status", color_discrete_map={"Zero Stock": "red", "With Stock": "green"}, hole=0.3)
                st.plotly_chart(fig_pie, use_container_width=True)
            output_file = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Processed Inventory", output_file, "processed_inventory.csv", "text/csv")

def process_inventory_file(file):
    try:
        df = pd.read_excel(file)
        required_columns = ["sku", "asin", "price", "quantity"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"❌ Missing columns: {', '.join(missing_columns)}")
            return None
        df = df[required_columns]
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
        return df
    except Exception as e:
        st.error(f"⚠️ Error processing file: {e}")
        return None

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
