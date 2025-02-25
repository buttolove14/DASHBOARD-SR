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
