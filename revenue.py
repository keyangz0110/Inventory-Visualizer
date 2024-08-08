import pandas as pd
import os
import threading
import re
import shutil
import uuid
import time
import streamlit as st
import matplotlib.pyplot as plt

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
def remove_directory_thread(path, time_limit=21600):
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
		raise FileNotFoundError("No file starting with '出库单报表' found in the specified folder.")
# Define the title of the web app
st.title("Revenue Analysis")
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
# User input for the start and end date
start_date = st.date_input("Please Select the Start Date")
end_date = st.date_input("Please Select the End Date")
# Generate date range between start and end date
date_range = pd.date_range(start_date, end_date).date
#
for date in date_range:
	# User input for total hours and hourly rate
	total_hours = st.text_input(f"请输入{date}的总工时: ")
	hourly_rate = st.text_input(f"请输入{date}的每个工时的费用: ")
# Load the data and keep only the required columns
uploaded_file = st.file_uploader("Upload Outbound Report File", type=['xlsx'])
# Start remove directory timer
remove_directory_thread(source_files_folder, time_limit=60)
# Save the uploaded files to the source_files folder
if uploaded_file:
	with open(os.path.join(source_files_folder, uploaded_file.name), "wb") as f:
		f.write(uploaded_file.getbuffer())
# List all files in the directory
all_files = os.listdir(source_files_folder)
# Define the regular expression pattern
uploaded_file_pattern = re.compile(r'^出库单报表.*\.xlsx$')
# Filter files that match the pattern
uploaded_file_matching_files = [f for f in all_files if uploaded_file_pattern.match(f)]

if st.button("Analyze"):
	# Read the files
	read_files()
	required_columns = [
		'出库单号', '外部单号', '出库单状态', '拣选单号', '出库货品数量', '创建时间',
		'汇波完成时间', '拣选完成时间', '复核完成时间', 'ItemWeight', '拣选策略'
	]
	data = uploaded_file[required_columns]

	# Drop rows with specific order statuses
	data = data[~data['出库单状态'].isin(['分配失败', '已取消', '已拣选', '待拣选', '拣选中'])]

	# Create new columns for date and hour
	data['创建时间'] = pd.to_datetime(data['创建时间'], errors='coerce')
	data['汇波完成时间'] = pd.to_datetime(data['汇波完成时间'], errors='coerce')
	data['拣选完成时间'] = pd.to_datetime(data['拣选完成时间'], errors='coerce')
	data['复核完成时间'] = pd.to_datetime(data['复核完成时间'], errors='coerce')

	data['创建日期'] = data['创建时间'].dt.date
	data['创建小时'] = data['创建时间'].dt.hour
	data['汇波日期'] = data['汇波完成时间'].dt.date
	data['汇波小时'] = data['汇波完成时间'].dt.hour
	data['拣选日期'] = data['拣选完成时间'].dt.date
	data['拣选小时'] = data['拣选完成时间'].dt.hour
	data['复核日期'] = data['复核完成时间'].dt.date
	data['复核小时'] = data['复核完成时间'].dt.hour

	# Filter data based on the selected date range
	start_datetime = pd.to_datetime(start_date) - pd.Timedelta(hours=12)
	end_datetime = pd.to_datetime(end_date) + pd.Timedelta(hours=11, minutes=59, seconds=59)
	filtered_data = data[(data['创建时间'] >= start_datetime) & (data['创建时间'] <= end_datetime)]

	# Calculate revenue for each order
	def calculate_order_revenue(group):
		weights = group['ItemWeight']
		max_weight = weights.max()
		num_packages = len(weights)

		if max_weight < 1:
			revenue = 0.7
		elif max_weight <= 5:
			revenue = 0.84
		else:
			revenue = 0.84 + (max_weight - 5) * 0.08

		if num_packages > 1:
			revenue += (num_packages - 1) * 0.4

		return revenue

	# Calculate revenue based on order number
	grouped = filtered_data.groupby('出库单号').apply(calculate_order_revenue).reset_index(name='收入')

	# Merge the revenue data with the filtered data
	filtered_data = pd.merge(filtered_data, grouped, on='出库单号')

	# Create a new column for the date
	filtered_data['统计日期'] = pd.cut(filtered_data['创建时间'],
									bins=pd.date_range(start_datetime, end_datetime + pd.Timedelta(days=1), freq='D'),
									labels=pd.date_range(start_date, end_date, freq='D').strftime('%Y-%m-%d'))

	# Calculate daily summary
	daily_summary = filtered_data.groupby('统计日期').agg(
		总收入=('收入', 'sum'),
		总包裹数=('出库货品数量', 'sum'),
		总订单数=('出库单号', 'nunique')
	).reset_index()

	# Retrieve the total hours and hourly rate for each day
	daily_summary['人力成本'] = 0.0
	daily_summary['盈亏'] = 0.0

	for index, row in daily_summary.iterrows():
		date_str = row['统计日期']
		total_hours = float(total_hours)
		hourly_rate = float(hourly_rate)
		daily_summary.at[index, '人力成本'] = total_hours * hourly_rate
		daily_summary.at[index, '盈亏'] = daily_summary.at[index, '总收入'] - daily_summary.at[index, '人力成本']

	# Visualize the daily summary
	fig, ax1 = plt.subplots(figsize=(12, 8))

	# Create the bar chart for total revenue
	bars = ax1.bar(daily_summary['统计日期'], daily_summary['总收入'], color='#4287f5', alpha=0.6, label='Gross Income')

	# Add data labels to the bar chart
	for bar in bars:
		yval = bar.get_height()
		ax1.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), va='bottom', ha='center')

	# Create the line chart for profit/loss
	ax2 = ax1.twinx()
	line = ax2.plot(daily_summary['统计日期'], daily_summary['盈亏'], marker='o', linestyle='-', color='#ff5733', label='Profit/Loss')

	# Add data labels to the line chart
	for i, txt in enumerate(daily_summary['盈亏']):
		ax2.annotate(round(txt, 2), (daily_summary['统计日期'][i], daily_summary['盈亏'][i]), textcoords="offset points", xytext=(0,10), ha='center')

	# Set labels and title
	ax1.set_xlabel('Date')
	ax1.set_ylabel('Gross Income ($)', color='#4287f5')
	ax2.set_ylabel('Profit/Loss ($)', color='#ff5733')
	plt.title('Daily Income and Profit/Loss')

	# Set grid
	ax1.grid(True)
	fig.tight_layout()
	fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))

	# Display the plot
	plt.xticks(rotation=45)
	st.pyplot(fig)

	# Show the daily summary
	st.write(daily_summary)
