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
st.title("Single Day Outbound Efficiency Analysis")
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
# User input for the current date
current_date = st.date_input("Please Select the Date")
# Convert format to 'YYYY/MM/DD'
current_date = current_date.strftime('%Y/%m/%d')
# Convert the input date to a datetime object
current_date = pd.to_datetime(current_date)
# Calculate the previous date based on the current date
previous_date = current_date - pd.Timedelta(days=1)
# Load the data and keep only the required columns
uploaded_file = st.file_uploader("Upload Outbound Report File", type=['xlsx'])
# Start remove directory timer
remove_directory_thread(source_files_folder)
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
# User input for shift hours
班次A工时 = st.text_input("请输入大夜班的总工时")
班次B工时 = st.text_input("请输入白班的总工时")

if st.button("Process File"):
	# Convert the input to float
	班次A工时 = float(班次A工时)
	班次B工时 = float(班次B工时)
	# Read the uploaded file
	read_files()
	# Define the required columns
	required_columns = [
		'出库单号', '外部单号', '出库单状态', '拣选单号', '出库货品数量', '创建时间',
		'汇波完成时间', '拣选完成时间', '复核完成时间', 'ItemWeight', '拣选策略'
	]
	data = uploaded_file[required_columns]

	# Drop records with '出库单状态' as '分配失败' and '已取消'
	data = data[~data['出库单状态'].isin(['分配失败', '已取消'])]

	# Create date and hour columns based on the specified time columns
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

	# Make sure the hour columns are of integer type and fill missing values
	data['创建小时'] = data['创建小时'].fillna(-1).astype(int)
	data['汇波小时'] = data['汇波小时'].fillna(-1).astype(int)
	data['拣选小时'] = data['拣选小时'].fillna(-1).astype(int)
	data['复核小时'] = data['复核小时'].fillna(-1).astype(int)

	# Define the shift based on the date and hour
	def determine_shift(date, hour):
		if date == current_date.date() and 6 <= hour < 18:
			return '白班'
		elif (date == previous_date.date() and 21 <= hour) or (date == current_date.date() and hour < 5):
			return '大夜班'
		else:
			return 'Other'

	data['班次'] = data.apply(lambda row: determine_shift(row['复核日期'], row['复核小时']), axis=1)

	# Calculate packing orders and items per hour
	hourly_summary = data.groupby(['复核日期', '复核小时', '班次']).agg(
		每小时复核打包单数=('出库单号', 'nunique'),
		每小时复核打包件数=('出库货品数量', 'sum')
	).reset_index()

	# Calculate individual shift's total orders and total items
	shift_summary = hourly_summary.groupby('班次').agg(
		复核打包完成单数=('每小时复核打包单数', 'sum'),
		复核打包完成件数=('每小时复核打包件数', 'sum'),
		平均每小时复核打包件数=('每小时复核打包件数', 'mean'),
		时间段=('复核日期', lambda x: ', '.join(x.astype(str)))
	).reset_index()

	# Calculate packing efficiency
	shift_summary['总工时'] = shift_summary['班次'].map({'大夜班':班次A工时, '白班':班次B工时}).fillna(0)
	shift_summary['件效'] = shift_summary['复核打包完成件数'] / shift_summary['总工时']

	# Calculate combined summary results
	overall_summary = shift_summary.sum(numeric_only=True).to_frame().T
	overall_summary['班次'] = '综合汇总'
	overall_summary['平均每小时复核打包件数'] = shift_summary[shift_summary['班次'].isin(['大夜班', '白班'])]['平均每小时复核打包件数'].mean()
	overall_summary['件效'] = overall_summary['复核打包完成件数'] / (班次A工时 + 班次B工时)

	# Combine summary results
	shift_summary = pd.concat([shift_summary, overall_summary], ignore_index=True)

	# Ensure the output_files directory is created only once
	if 'output_files_folder' not in st.session_state:
		# Generate a unique identifier for the session
		session_id = str(uuid.uuid4())
		output_files_folder = f'output_files_{session_id}'
		st.session_state['output_files_folder'] = output_files_folder
	else:
		output_files_folder = st.session_state['output_files_folder']
	# Create the directory if it doesn't exist
	if not os.path.exists(output_files_folder):
		os.makedirs(output_files_folder)
	# Start remove directory timer
	remove_directory_thread(output_files_folder)
	# Define new file name
	new_filename = f"summary-result-{current_date.date()}.xlsx"
	# Save the summary results to an Excel file
	output_file = f'{output_files_folder}/{new_filename}'
	with pd.ExcelWriter(output_file) as writer:
		hourly_summary.to_excel(writer, sheet_name='Hourly Summary', index=False)
		shift_summary.to_excel(writer, sheet_name='Shift Summary', index=False)

	st.success(f"Summary results saved to {output_file}")

	# Provide a download button for the saved file
	with open(os.path.join(output_files_folder, new_filename), "rb") as file:
		btn = st.download_button(
			label="Download Generated Results",
			data=file,
			file_name=new_filename,
			mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
		)

	# Show the shift summary
	st.write(shift_summary)
