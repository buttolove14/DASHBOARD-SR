import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

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
