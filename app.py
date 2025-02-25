import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def process_order_report():
import streamlit as st
import pandas as pd
import plotly.express as px

def process_order_report():
    # Streamlit App Title
    st.markdown("<h1 style='text-align: center; color: #4A90E2;'>📊 Amazon Order Report Dashboard</h1>", unsafe_allow_html=True)

    # File Uploader
    st.sidebar.header("Upload Data")
    uploaded_file = st.sidebar.file_uploader("Upload Amazon Order Report", type=["csv", "xlsx"])

    if uploaded_file:
        # Load Data
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)

        # Ensure Required Columns Exist
        required_columns = ["purchase-date", "order-status", "fulfillment-channel", "item-price", "ship-city", "sku", "product-name"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing columns: {', '.join(missing_columns)}")
            return

        # Convert Date Columns to Datetime and Remove Timezone
        df["purchase-date"] = pd.to_datetime(df["purchase-date"], errors='coerce').dt.tz_localize(None)
        df["last-updated-date"] = pd.to_datetime(df["last-updated-date"], errors='coerce').dt.tz_localize(None)

        # Sidebar Filters
        st.sidebar.header("Filters")
        order_status = st.sidebar.multiselect("Order Status", df["order-status"].dropna().unique(), default=df["order-status"].dropna().unique())
        fulfillment_channel = st.sidebar.multiselect("Fulfillment Channel", df["fulfillment-channel"].dropna().unique(), default=df["fulfillment-channel"].dropna().unique())

        # Date Range Selection
        min_date, max_date = df["purchase-date"].min().date(), df["purchase-date"].max().date()
        date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

        start_date, end_date = pd.Timestamp(date_range[0]).tz_localize(None), pd.Timestamp(date_range[1]).tz_localize(None)

        # Apply Filters
        filtered_df = df[
            df["order-status"].isin(order_status) &
            df["fulfillment-channel"].isin(fulfillment_channel) &
            df["purchase-date"].between(start_date, end_date)
        ]

        if filtered_df.empty:
            st.warning("No records found matching the selected filters.")
            return

        # Summary Metrics
        total_orders = filtered_df.shape[0]
        total_revenue = filtered_df["item-price"].sum()
        cancelled_orders = filtered_df[filtered_df["order-status"] == "Cancelled"].shape[0]

        # Display Summary
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Orders", total_orders)
        col2.metric("Total Revenue", f"Rs.{total_revenue:,.2f}")
        col3.metric("Cancelled Orders", cancelled_orders)

        # Orders Over Time Chart
        orders_by_date = filtered_df.groupby(filtered_df["purchase-date"].dt.date).size().reset_index(name="Orders")
        fig = px.line(orders_by_date, x="purchase-date", y="Orders", title="📈 Orders Over Time", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        # Top Cities Chart
        top_cities = filtered_df["ship-city"].value_counts().head(10).reset_index()
        top_cities.columns = ["City", "Orders"]
        fig = px.bar(top_cities, x="City", y="Orders", title="🌆 Top Shipping Cities", color="Orders", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

        # Top Selling Products
        repeated_products = filtered_df["product-name"].value_counts().reset_index()
        repeated_products.columns = ["Product Name", "Purchase Count"]
        st.markdown("### 🔥 Most Repeatedly Purchased Products")
        st.dataframe(repeated_products.head(10))

        # Top Selling SKUs
        top_skus = filtered_df["sku"].value_counts().reset_index()
        top_skus.columns = ["SKU", "Order Count"]
        st.markdown("### 🏆 Top Selling SKUs")
        st.dataframe(top_skus.head(10))

def process_inventory():
    """Handles the UI and processing of inventory reports in Streamlit."""
    st.markdown("<h1>📊Amazon Inventory Dashboard</h1>", unsafe_allow_html=True)
    st.write("Upload your Excel file to generate insights on inventory.")

    # File uploader inside the function
    uploaded_file = st.file_uploader("📂 Choose an Excel file", type=["xlsx"])

    if uploaded_file is not None:
        df = process_inventory_file(uploaded_file)  # Call the helper function

        if df is not None:
            st.markdown("### 📝 Processed Inventory Report")
            st.dataframe(df, height=600, use_container_width=True)

            # Key Metrics
            total_inventory = int(df["quantity"].sum())
            total_value = int((df["price"] * df["quantity"]).sum())
            avg_price = round(df["price"].mean(), 2)
            zero_inventory_skus = int((df["quantity"] == 0).sum())
            available_skus = int((df["quantity"] > 0).sum())

            # Display Key Metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("📦 Total Inventory", f"{total_inventory:,}")
            col2.metric("💰 Total Value", f"₹{total_value:,}")
            col3.metric("📊 Avg. Price", f"₹{avg_price:,.2f}")
            col4.metric("🚫 Zero Stock SKUs", f"{zero_inventory_skus:,}")
            col5.metric("✅ Available SKUs", f"{available_skus:,}")

            # Pie Chart for Stock Distribution
            stock_data = pd.DataFrame({
                "Stock Status": ["Zero Stock", "With Stock"],
                "Count": [zero_inventory_skus, available_skus]
            })

            if zero_inventory_skus > 0 or available_skus > 0:
                fig_pie = px.pie(
                    stock_data, 
                    names="Stock Status", 
                    values="Count", 
                    title="📊 Zero Stock vs With Stock Distribution", 
                    color="Stock Status",
                    color_discrete_map={"Zero Stock": "red", "With Stock": "green"},
                    hole=0.3
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            # Download Processed Data
            output_file = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Processed Inventory", output_file, "processed_inventory.csv", "text/csv")

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
