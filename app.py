import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Set Streamlit Page Configuration
st.set_page_config(page_title="Amazon Dashboard", page_icon="📊", layout="wide")

# Custom CSS for Aesthetic UI
st.markdown(
    """
    <style>
        .css-18e3th9 {
            padding-top: 0rem;
        }
        .css-1d391kg {
            padding-top: 1rem;
        }
        .big-font {
            font-size:20px !important;
            font-weight: bold;
            color: #4A90E2;
        }
        .stMetric {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        }
    </style>
    """,
    unsafe_allow_html=True
)


def load_data(uploaded_file):
    """Loads CSV or Excel file into a Pandas DataFrame."""
    return pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)

def process_order_report():
    """Processes and visualizes the Amazon order report."""
    st.markdown("<h1 style='text-align: center; color: #4A90E2;'>📊 Amazon Order Report Dashboard</h1>", unsafe_allow_html=True)
    uploaded_file = st.sidebar.file_uploader("Upload Amazon Order Report", type=["csv", "xlsx"])
    
    if uploaded_file:
        df = load_data(uploaded_file)
        required_columns = ["purchase-date", "order-status", "fulfillment-channel", "item-price", "ship-city", "sku", "product-name"]
        
        if missing_columns := [col for col in required_columns if col not in df.columns]:
            st.error(f"Missing columns: {', '.join(missing_columns)}")
            return
        
        df["purchase-date"] = pd.to_datetime(df["purchase-date"], errors='coerce').dt.tz_localize(None)
        min_date, max_date = df["purchase-date"].min().date(), df["purchase-date"].max().date()
        
        order_status = st.sidebar.multiselect("Order Status", df["order-status"].dropna().unique(), default=df["order-status"].dropna().unique())
        fulfillment_channel = st.sidebar.multiselect("Fulfillment Channel", df["fulfillment-channel"].dropna().unique(), default=df["fulfillment-channel"].dropna().unique())
        date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])
        
        filtered_df = df[
            df["order-status"].isin(order_status) &
            df["fulfillment-channel"].isin(fulfillment_channel) &
            df["purchase-date"].between(pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]))
        ]
        
        if filtered_df.empty:
            st.warning("No records found matching the selected filters.")
            return
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Orders", filtered_df.shape[0])
        col2.metric("Total Revenue", f"Rs.{filtered_df['item-price'].sum():,.2f}")
        col3.metric("Cancelled Orders", filtered_df[filtered_df["order-status"] == "Cancelled"].shape[0])
        
        orders_by_date = filtered_df.groupby(filtered_df["purchase-date"].dt.date).size().reset_index(name="Orders")
        st.plotly_chart(px.line(orders_by_date, x="purchase-date", y="Orders", title="📈 Orders Over Time", markers=True), use_container_width=True)
        
        top_cities = filtered_df["ship-city"].value_counts().head(10).reset_index()
        top_cities.columns = ["City", "Orders"]
        st.plotly_chart(px.bar(top_cities, x="City", y="Orders", title="🌆 Top Shipping Cities", color="Orders", text_auto=True), use_container_width=True)
        
        st.markdown("### 🔥 Most Repeatedly Purchased Products")
        st.dataframe(filtered_df["product-name"].value_counts().reset_index().rename(columns={"index": "Product Name", "product-name": "Purchase Count"}).head(10))
        
        st.markdown("### 🏆 Top Selling SKUs")
        st.dataframe(filtered_df["sku"].value_counts().reset_index().rename(columns={"index": "SKU", "sku": "Order Count"}).head(10))

def process_inventory():
    """Processes and visualizes the Amazon inventory report."""
    st.markdown("<h1>📊 Amazon Inventory Dashboard</h1>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("📂 Choose an Excel file", type=["xlsx"])
    
    if uploaded_file:
        df = load_data(uploaded_file)
        total_inventory, total_value = df["quantity"].sum(), (df["price"] * df["quantity"]).sum()
        avg_price, zero_inventory_skus, available_skus = df["price"].mean(), (df["quantity"] == 0).sum(), (df["quantity"] > 0).sum()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("📦 Total Inventory", f"{total_inventory:,}")
        col2.metric("💰 Total Value", f"₹{total_value:,}")
        col3.metric("📊 Avg. Price", f"₹{avg_price:,.2f}")
        col4.metric("🚫 Zero Stock SKUs", f"{zero_inventory_skus:,}")
        col5.metric("✅ Available SKUs", f"{available_skus:,}")
        
        stock_data = pd.DataFrame({"Stock Status": ["Zero Stock", "With Stock"], "Count": [zero_inventory_skus, available_skus]})
        st.plotly_chart(px.pie(stock_data, names="Stock Status", values="Count", title="📊 Zero Stock vs With Stock", color="Stock Status", color_discrete_map={"Zero Stock": "red", "With Stock": "green"}, hole=0.3), use_container_width=True)

def process_return_report():
    st.markdown("<h2 style='text-align: center; color: #E24A4A;'>🔄 Amazon Return Report Dashboard</h2>", unsafe_allow_html=True)

    # File Uploader
    uploaded_file = st.sidebar.file_uploader("Upload Amazon Return Report", type=["csv", "xlsx"])

    if uploaded_file:
        # Read the file
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.markdown("### 📋 Raw Data Preview")
        st.dataframe(df.head())

        # Standardize Column Names
        df.columns = df.columns.str.strip().str.lower()

        # Convert columns to datetime
        date_columns = ["order date", "return request date", "return delivery date", "safet claim creation time"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Convert numeric columns to appropriate types
        numeric_columns = ["refunded amount", "order amount"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Filters
        st.sidebar.header("Filters")
        return_status = df["return request status"].dropna().unique() if "return request status" in df.columns else []
        return_reason = df["return reason"].dropna().unique() if "return reason" in df.columns else []

        if return_status.any():
            selected_status = st.sidebar.multiselect("Filter by Return Request Status", options=return_status, default=return_status)
        if return_reason.any():
            selected_reason = st.sidebar.multiselect("Filter by Return Reason", options=return_reason, default=return_reason)

        # Date Filter
        if "order date" in df.columns:
            date_range = st.sidebar.date_input("Select Order Date Range", [df["order date"].min().date(), df["order date"].max().date()])
            start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        else:
            start_date, end_date = None, None

        # Apply Filters
        filtered_df = df.copy()
        if "return request status" in df.columns and selected_status:
            filtered_df = filtered_df[filtered_df["return request status"].isin(selected_status)]
        if "return reason" in df.columns and selected_reason:
            filtered_df = filtered_df[filtered_df["return reason"].isin(selected_reason)]
        if "order date" in df.columns and start_date and end_date:
            filtered_df = filtered_df[filtered_df["order date"].between(start_date, end_date)]

        st.markdown("### 🔍 Filtered Data Preview")
        st.dataframe(filtered_df.head())

        # Summary Metrics
        total_returns = filtered_df.shape[0]
        total_refunded_amount = filtered_df["refunded amount"].sum() if "refunded amount" in filtered_df.columns else 0
        total_order_amount = filtered_df["order amount"].sum() if "order amount" in filtered_df.columns else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Return Requests", total_returns)
        with col2:
            st.metric("Total Refunded Amount", f"Rs.{total_refunded_amount:,.2f}")
        with col3:
            st.metric("Total Order Amount", f"Rs.{total_order_amount:,.2f}")

        # Returns Over Time Chart
        if "return request date" in filtered_df.columns:
            returns_by_date = filtered_df.groupby(filtered_df["return request date"].dt.date).size().reset_index(name="Returns")
            fig = px.line(returns_by_date, x="return request date", y="Returns", title="📉 Return Requests Over Time", markers=True)
            st.plotly_chart(fig, use_container_width=True)

        # Top Return Reasons
        if "return reason" in filtered_df.columns:
            top_reasons = filtered_df["return reason"].value_counts().reset_index()
            top_reasons.columns = ["Return Reason", "Count"]
            fig = px.bar(top_reasons.head(10), x="Return Reason", y="Count", title="🔝 Top Return Reasons", color="Count", text_auto=True)
            st.plotly_chart(fig, use_container_width=True)

        # Top Returned SKUs
        if "merchant sku" in filtered_df.columns:
            top_returned_skus = filtered_df["merchant sku"].value_counts().reset_index()
            top_returned_skus.columns = ["SKU", "Return Count"]
            st.markdown("### 🏆 Top Returned SKUs")
            st.dataframe(top_returned_skus.head(10))

        # Top Returned Product Names
        if "item name" in filtered_df.columns:
            top_returned_products = filtered_df["item name"].value_counts().reset_index()
            top_returned_products.columns = ["Product Name", "Return Count"]
            st.markdown("### 🔥 Most Frequently Returned Products")
            st.dataframe(top_returned_products.head(10))

def main():
    st.sidebar.title("📌 Navigation")
    page = st.sidebar.radio("Go to", ["Order Report", "Inventory Report", "Return Report"])
    
    if page == "Order Report":
        process_order_report()
    elif page == "Inventory Report":
        process_inventory()
    elif page == "Return Report":
        process_return_report()

# Add footer in the sidebar
st.sidebar.markdown("🚀 **Work done by Tech Assassins - Seller Rocket**")

if __name__ == "__main__":
    main()
