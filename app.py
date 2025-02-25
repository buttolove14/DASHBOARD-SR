import streamlit as st
from order import process_order_report
from returns import process_return_report
from inventory import process_inventory

st.sidebar.title("📌 Dashboard Menu")
menu = st.sidebar.radio("Select a Report:", ["Order Report", "Return Report", "Inventory Report"])

if menu == "Order Report":
    process_order_report()
elif menu == "Return Report":
    process_return_report()
elif menu == "Inventory Report":
    process_inventory()  # Now this works correctly

# Add footer in the sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("🚀 **Work done by Tech Assassins - Seller Rocket**")
