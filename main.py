import hmac
import streamlit as st

def check_password():
	# Return True if the user provides the correct password
	def password_entered():
		# Checks whether a password entered by the user is correct
		if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
			st.session_state["password_correct"] = True
			del st.session_state["password"]  # Do not store the password
		else:
			st.session_state["password_correct"] = False

	# Return True if the password is validated
	if st.session_state.get("password_correct", False):
		return True
	
	# Show input for password
	st.text_input(
		"Password", type="password", on_change=password_entered, key="password"
	)

	# Show error message if password is incorrect
	if "password_correct" in st.session_state:
		st.error("😕 Password incorrect")
	# Return False if password is not validated
	return False

if not check_password():
	# Do not continue if check_password is not True
	st.stop()

# Main streamlit app
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
