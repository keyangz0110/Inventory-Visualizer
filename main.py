import streamlit as st

inventory_visualizer_page = st.Page("inventory_visualizer.py", title="Inventory Visualizer", icon=":material/inventory_2:")
outbound_efficiency_page = st.Page("ob_efficiency.py", title="Single Day Outbound Efficiency", icon=":material/outbound:")
multiple_outbound_efficiency_page = st.Page("multiple_ob_efficiency.py", title="Multi-Day Outbound Efficiency", icon=":material/outbound:")

pg = st.navigation([inventory_visualizer_page, outbound_efficiency_page, multiple_outbound_efficiency_page])
st.set_page_config(page_title="WMS Utilities", page_icon=":material/monitoring:")
pg.run()
