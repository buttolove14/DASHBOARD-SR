import streamlit as st
import pandas as pd
import plotly.express as px

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

def process_inventory_file(file):
    """Processes the uploaded inventory file and returns a cleaned dataframe."""
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
