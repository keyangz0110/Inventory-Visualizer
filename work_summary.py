import pandas as pd
import os
import threading
import re
import shutil
import uuid
import time
import streamlit as st

# Remove directory with timer function
def remove_directory(path, time_limit=21600):  # Default time limit is 6 hours (21600 seconds)
	while True:
		# Get the current time
		current_time = time.time()
		# Check if the directory exists
		if os.path.exists(path):
			# Get the age of the directory
			directory_age = current_time - os.path.getmtime(path)
			# Check if the directory is older than the time limit
			if directory_age > time_limit:
				try:
					# Remove the directory
					shutil.rmtree(path)
					# Print the message
					print(f"Removed directory: {path}")
					break  # Exit the loop after removing the directory
				except OSError as e:
					# Print the error message
					print(f"Error: {e.strerror}")
					break  # Exit the loop if an error occurs
		else:
			print(f"Directory does not exist: {path}")
			break  # Exit the loop if the directory does not exist
		# Sleep for a period before checking again
		time.sleep(3600)  # Check every 1 hour
# Start the remove_directory function in a separate thread
def remove_directory_thread(path, time_limit=60):
	thread = threading.Thread(target=remove_directory, args=(path, time_limit))
	thread.daemon = True  # Set as a daemon thread to exit when the main program exits
	thread.start()
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
# Define the title of the web app
st.title("Operator Work Summary Analysis")
# Ensure the source_files directory is created only once
if 'source_files_folder' not in st.session_state:
	# Generate a unique identifier for the session
	session_id = str(uuid.uuid4())
	source_files_folder = f'source_files_{session_id}'
	st.session_state['source_files_folder'] = source_files_folder
else:
	source_files_folder = st.session_state['source_files_folder']
# Create the directory if it doesn't exist
if not os.path.exists(source_files_folder):
	os.makedirs(source_files_folder)
# Load the data and keep only the required columns
uploaded_file = st.file_uploader("Upload Work Summary File", type=['xlsx'])
# Create three radio buttons
selection = st.radio("Select Report Type", ["出库拣选", "出库复核"], horizontal=True)
# Start remove directory timer
remove_directory_thread(source_files_folder)
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
		st.write("出库拣选总表")
		st.write(pivot_table)
		# Create two separate pivot tables for '作业效率' and '总作业件数'
		# For filter entries, combine '出库拣选/普通单件' and '出库拣选/混合包裹' together
		# For values, sum the values for each user
		# Create a pivot table for '作业效率'
		pivot_table_efficiency = pd.pivot_table(uploaded_file, values='作业效率', index='用户名', columns='任务类型', aggfunc='sum')
		# Remove user name 'system' and 'wujiahua'
		pivot_table_efficiency = pivot_table_efficiency.drop(index=['system', 'wujiahua'], errors='ignore')
		# Calculate Q1 (25th percentile) and Q3 (75th percentile)
		Q1 = pivot_table_efficiency.quantile(0.25)
		Q3 = pivot_table_efficiency.quantile(0.75)
		# Calculate IQR
		IQR = Q3 - Q1
		# Filter out the outliers
		pivot_table_efficiency = pivot_table_efficiency[~((pivot_table_efficiency < (Q1 - 1.5 * IQR)) | (pivot_table_efficiency > (Q3 + 1.5 * IQR))).any(axis=1)]
		# Fill NaN values with 0
		pivot_table_efficiency = pivot_table_efficiency.fillna(0)
		# Combine '出库拣选/普通单件' and '出库拣选/混合包裹' together
		pivot_table_efficiency['出库拣选/普通+混合'] = pivot_table_efficiency['出库拣选/普通单件'] + pivot_table_efficiency['出库拣选/混合包裹']
		pivot_table_efficiency = pivot_table_efficiency.drop(columns=['出库拣选/普通单件', '出库拣选/混合包裹', '出库拣选/其他'], errors='ignore')
		# Create a pivot table for '总作业件数'
		pivot_table_total = pd.pivot_table(uploaded_file, values='总作业件数', index='用户名', columns='任务类型', aggfunc='sum')
		# Remove user name 'system' and 'wujiahua'
		pivot_table_total = pivot_table_total.drop(index=['system', 'wujiahua'], errors='ignore')
		# Calculate Q1 (25th percentile) and Q3 (75th percentile)
		Q1 = pivot_table_total.quantile(0.25)
		Q3 = pivot_table_total.quantile(0.75)
		# Calculate IQR
		IQR = Q3 - Q1
		# Filter out the outliers
		pivot_table_total = pivot_table_total[~((pivot_table_total < (Q1 - 1.5 * IQR)) | (pivot_table_total > (Q3 + 1.5 * IQR))).any(axis=1)]
		# Fill NaN values with 0
		pivot_table_total = pivot_table_total.fillna(0)
		# Combine '出库拣选/普通单件' and '出库拣选/混合包裹' together
		pivot_table_total['出库拣选/普通+混合'] = pivot_table_total['出库拣选/普通单件'] + pivot_table_total['出库拣选/混合包裹']
		pivot_table_total = pivot_table_total.drop(columns=['出库拣选/普通单件', '出库拣选/混合包裹', '出库拣选/其他'], errors='ignore')
		# Display the pivot tables
		st.write("出库拣选作业效率")
		st.write(pivot_table_efficiency)
		# Create a bar chart for '作业效率'
		# For an individual user, display the '作业效率' for each task type
		st.write("出库拣选作业效率柱状图")
		st.bar_chart(pivot_table_efficiency, stack=False, color=['#4287f5', '#ff5733'])
		# Display the pivot tables
		st.write("出库拣选总作业件数")
		st.write(pivot_table_total)
		# Create a bar chart for '总作业件数'
		# For an individual user, display the '总作业件数' for each task type
		st.write("出库拣选总作业件数柱状图")
		st.bar_chart(pivot_table_total, stack=False, color=['#4287f5', '#ff5733'])
	elif selection == "出库复核":
		# Create pivot table with the required columns:
		# '用户名' as Axis, '作业效率' and '总作业件数' as Values, '任务类型' as Filters
		pivot_table = pd.pivot_table(uploaded_file, values=['作业效率', '总作业件数'], index='用户名', columns='任务类型', aggfunc='sum')
		# Fill NaN values with 0
		pivot_table = pivot_table.fillna(0)
		# Flatten the MultiIndex columns
		pivot_table.columns = ['_'.join(col).strip() for col in pivot_table.columns.values]
		# Drop rows that values exceeds average value * 2
		# Calculate the average value for each column
		average_values = pivot_table.mean()
		# Drop rows that values exceeds average value * 2
		pivot_table = pivot_table[(pivot_table < average_values * 2).all(axis=1)]
		# Display the pivot table
		st.write("出库复核总表")
		st.write(pivot_table)
		# Create two separate pivot tables for '作业效率' and '总作业件数'
		# For filter entries, combine '出库拣选/普通单件' and '出库拣选/混合包裹' together
		# For values, sum the values for each user
		# Create a pivot table for '作业效率'
		pivot_table_efficiency = pd.pivot_table(uploaded_file, values='作业效率', index='用户名', columns='任务类型', aggfunc='sum')
		# Remove user name 'system' and 'wujiahua'
		pivot_table_efficiency = pivot_table_efficiency.drop(index=['system', 'wujiahua'], errors='ignore')
		# Calculate Q1 (25th percentile) and Q3 (75th percentile)
		Q1 = pivot_table_efficiency.quantile(0.25)
		Q3 = pivot_table_efficiency.quantile(0.75)
		# Calculate IQR
		IQR = Q3 - Q1
		# Filter out the outliers
		pivot_table_efficiency = pivot_table_efficiency[~((pivot_table_efficiency < (Q1 - 1.5 * IQR)) | (pivot_table_efficiency > (Q3 + 1.5 * IQR))).any(axis=1)]
		# Fill NaN values with 0
		pivot_table_efficiency = pivot_table_efficiency.fillna(0)
		# Combine '出库拣选/普通单件' and '出库拣选/混合包裹' together
		pivot_table_efficiency['出库复核/普通+混合'] = pivot_table_efficiency['出库复核/普通单件'] + pivot_table_efficiency['出库复核/混合包裹']
		pivot_table_efficiency = pivot_table_efficiency.drop(columns=['出库复核/普通单件', '出库复核/混合包裹', '出库复核/其他'], errors='ignore')
		# Create a pivot table for '总作业件数'
		pivot_table_total = pd.pivot_table(uploaded_file, values='总作业件数', index='用户名', columns='任务类型', aggfunc='sum')
		# Remove user name 'system' and 'wujiahua'
		pivot_table_total = pivot_table_total.drop(index=['system', 'wujiahua'], errors='ignore')
		# Calculate Q1 (25th percentile) and Q3 (75th percentile)
		Q1 = pivot_table_total.quantile(0.25)
		Q3 = pivot_table_total.quantile(0.75)
		# Calculate IQR
		IQR = Q3 - Q1
		# Filter out the outliers
		pivot_table_total = pivot_table_total[~((pivot_table_total < (Q1 - 1.5 * IQR)) | (pivot_table_total > (Q3 + 1.5 * IQR))).any(axis=1)]
		# Fill NaN values with 0
		pivot_table_total = pivot_table_total.fillna(0)
		# Combine '出库拣选/普通单件' and '出库拣选/混合包裹' together
		pivot_table_total['出库复核/普通+混合'] = pivot_table_total['出库复核/普通单件'] + pivot_table_total['出库复核/混合包裹']
		pivot_table_total = pivot_table_total.drop(columns=['出库复核/普通单件', '出库复核/混合包裹', '出库复核/其他'], errors='ignore')
		# Display the pivot tables
		st.write("出库复核作业效率")
		st.write(pivot_table_efficiency)
		# Create a bar chart for '作业效率'
		# For an individual user, display the '作业效率' for each task type
		st.write("出库复核作业效率柱状图")
		st.bar_chart(pivot_table_efficiency, stack=False, color=['#4287f5', '#ff5733'])
		# Display the pivot tables
		st.write("出库复核总作业件数")
		st.write(pivot_table_total)
		# Create a bar chart for '总作业件数'
		# For an individual user, display the '总作业件数' for each task type
		st.write("出库复核总作业件数柱状图")
		st.bar_chart(pivot_table_total, stack=False, color=['#4287f5', '#ff5733'])