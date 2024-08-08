import streamlit as st

inventory_visualizer_page = st.Page("inventory_visualizer.py", title="Inventory Visualizer", icon=":material/inventory_2:")
outbound_efficiency_page = st.Page("ob_efficiency.py", title="Single Day Outbound Efficiency", icon=":material/outbound:")
multiple_outbound_efficiency_page = st.Page("multiple_ob_efficiency.py", title="Multi-Day Outbound Efficiency", icon=":material/outbound:")
work_summary_page = st.Page("work_summary.py", title="Operator Work Summary", icon=":material/person_apron:")
revenue_analysis_page = st.Page("revenue.py", title="Revenue Analysis", icon=":material/payments:")
worker_schedule_page = st.Page("worker_schedule.py", title="Worker Schedule", icon=":material/edit_calendar:")

pg = st.navigation([inventory_visualizer_page,
                    outbound_efficiency_page,
                    multiple_outbound_efficiency_page,
                    work_summary_page,
                    revenue_analysis_page,
                    worker_schedule_page])
st.set_page_config(page_title="WMS Utilities", page_icon=":material/monitoring:")
pg.run()
