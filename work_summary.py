import pandas as pd
import os
import re
import shutil
import uuid
import time
import streamlit as st

# Remove directory with timer function
def remove_directory(path):
	# Get the current time
	current_time = time.time()
	# Get the age of the directory
	directory_age = current_time - os.path.getmtime(path)
	# Check if the directory is older than 6 hours
	if directory_age > 21600:  # 21600 seconds = 6 hours
		try:
			# Remove the directory
			shutil.rmtree(path)
			# Print the message
			print(f"Removed directory: {path}")
		except OSError as e:
			# Print the error message
			print(f"Error: {e.strerror}")
# Reset function
def reset():
	# Remove the source_files folder
	shutil.rmtree("source_files", ignore_errors=True)
# Read files function
def read_files():
	global uploaded_file
	# Check if any matching files are found
	if uploaded_file_matching_files:
			# Construct the full path of the first matching file
			uploaded_file_file_path = os.path.join(source_files_folder, uploaded_file_matching_files[0])
			# Read the first matching file
			uploaded_file = pd.read_excel(uploaded_file_file_path)
	else:
		raise FileNotFoundError("No file starting with '员工作业汇总表' found in the specified folder.")
# Reset the web app
# reset()
# Define the title of the web app
st.title("Operator Work Summary Analysis")
# Generate a unique identifier for the session
session_id = str(uuid.uuid4())
# Load the data and keep only the required columns
uploaded_file = st.file_uploader("Upload Work Summary File", type=['xlsx'])
# Create three radio buttons
selection = st.radio("Select Report Type", ["出库拣选", "出库复核"], horizontal=True)
# Define source_files folder
source_files_folder = f'source_files_{session_id}'
# Create the directory if it doesn't exist
os.makedirs(source_files_folder, exist_ok=True)
# Start remove directory timer
remove_directory(source_files_folder)
# Save the uploaded files to the source_files folder
if uploaded_file:
	with open(os.path.join(source_files_folder, uploaded_file.name), "wb") as f:
		f.write(uploaded_file.getbuffer())
# List all files in the directory
all_files = os.listdir(source_files_folder)
# Define the regular expression pattern
uploaded_file_pattern = re.compile(r'^员工作业汇总表.*\.xlsx$')
# Filter files that match the pattern
uploaded_file_matching_files = [f for f in all_files if uploaded_file_pattern.match(f)]

if st.button("Analyze"):
	# Read the files
	read_files()
	if selection == "出库拣选":
		# Create pivot table with the required columns:
		# '用户名' as Axis, '作业效率' and '总作业件数' as Values, '任务类型' as Filters
		pivot_table = pd.pivot_table(uploaded_file, values=['作业效率', '总作业件数'], index='用户名', columns='任务类型', aggfunc='sum')
		# Fill NaN values with 0
		pivot_table = pivot_table.fillna(0)
		# Flatten the MultiIndex columns
		pivot_table.columns = ['_'.join(col).strip() for col in pivot_table.columns.values]
		# Display the pivot table
		st.write("总表")
		st.write(pivot_table)
		# Create two separate pivot tables for '作业效率' and '总作业件数'
		# For filter entries, combine '出库拣选/普通单件' and '出库拣选/混合包裹' together
		# For values, sum the values for each user
		# Create a pivot table for '作业效率'
		pivot_table_efficiency = pd.pivot_table(uploaded_file, values='作业效率', index='用户名', columns='任务类型', aggfunc='sum')
		# Fill NaN values with 0
		pivot_table_efficiency = pivot_table_efficiency.fillna(0)
		# Combine '出库拣选/普通单件' and '出库拣选/混合包裹' together
		pivot_table_efficiency['出库拣选/普通+混合'] = pivot_table_efficiency['出库拣选/普通单件'] + pivot_table_efficiency['出库拣选/混合包裹']
		pivot_table_efficiency = pivot_table_efficiency.drop(columns=['出库拣选/普通单件', '出库拣选/混合包裹'])
		# Create a pivot table for '总作业件数'
		pivot_table_total = pd.pivot_table(uploaded_file, values='总作业件数', index='用户名', columns='任务类型', aggfunc='sum')
		# Fill NaN values with 0
		pivot_table_total = pivot_table_total.fillna(0)
		# Combine '出库拣选/普通单件' and '出库拣选/混合包裹' together
		pivot_table_total['出库拣选/普通+混合'] = pivot_table_total['出库拣选/普通单件'] + pivot_table_total['出库拣选/混合包裹']
		pivot_table_total = pivot_table_total.drop(columns=['出库拣选/普通单件', '出库拣选/混合包裹'])
		# Display the pivot tables
		st.write("作业效率")
		st.write(pivot_table_efficiency)
		# Create a bar chart for '作业效率'
		# For an individual user, display the '作业效率' for each task type
		st.bar_chart(pivot_table_efficiency, stack=False, color=['#4287f5', '#ff5733'])
		# Display the pivot tables
		st.write("总作业件数")
		st.write(pivot_table_total)
		# Create a bar chart for '总作业件数'
		# For an individual user, display the '总作业件数' for each task type
		st.bar_chart(pivot_table_total, stack=False, color=['#4287f5', '#ff5733'])
	elif selection == "出库复核":
		# Create pivot table with the required columns:
		# '用户名' as Axis, '作业效率' and '总作业件数' as Values, '任务类型' as Filters
		pivot_table = pd.pivot_table(uploaded_file, values=['作业效率', '总作业件数'], index='用户名', columns='任务类型', aggfunc='sum')
		# Fill NaN values with 0
		pivot_table = pivot_table.fillna(0)
		# Flatten the MultiIndex columns
		pivot_table.columns = ['_'.join(col).strip() for col in pivot_table.columns.values]
		# Display the pivot table
		st.write("总表")
		st.write(pivot_table)
		# Create two separate pivot tables for '作业效率' and '总作业件数'
		# For filter entries, combine '出库拣选/普通单件' and '出库拣选/混合包裹' together
		# For values, sum the values for each user
		# Create a pivot table for '作业效率'
		pivot_table_efficiency = pd.pivot_table(uploaded_file, values='作业效率', index='用户名', columns='任务类型', aggfunc='sum')
		# Fill NaN values with 0
		pivot_table_efficiency = pivot_table_efficiency.fillna(0)
		# Combine '出库拣选/普通单件' and '出库拣选/混合包裹' together
		pivot_table_efficiency['出库复核/普通+混合'] = pivot_table_efficiency['出库复核/普通单件'] + pivot_table_efficiency['出库复核/混合包裹']
		pivot_table_efficiency = pivot_table_efficiency.drop(columns=['出库复核/普通单件', '出库复核/混合包裹'])
		# Create a pivot table for '总作业件数'
		pivot_table_total = pd.pivot_table(uploaded_file, values='总作业件数', index='用户名', columns='任务类型', aggfunc='sum')
		# Fill NaN values with 0
		pivot_table_total = pivot_table_total.fillna(0)
		# Combine '出库拣选/普通单件' and '出库拣选/混合包裹' together
		pivot_table_total['出库复核/普通+混合'] = pivot_table_total['出库复核/普通单件'] + pivot_table_total['出库复核/混合包裹']
		pivot_table_total = pivot_table_total.drop(columns=['出库复核/普通单件', '出库复核/混合包裹'])
		# Display the pivot tables
		st.write("作业效率")
		st.write(pivot_table_efficiency)
		# Create a bar chart for '作业效率'
		# For an individual user, display the '作业效率' for each task type
		st.bar_chart(pivot_table_efficiency, stack=False, color=['#4287f5', '#ff5733'])
		# Display the pivot tables
		st.write("总作业件数")
		st.write(pivot_table_total)
		# Create a bar chart for '总作业件数'
		# For an individual user, display the '总作业件数' for each task type
		st.bar_chart(pivot_table_total, stack=False, color=['#4287f5', '#ff5733'])