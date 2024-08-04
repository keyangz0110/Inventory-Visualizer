import pandas as pd
import os
import re
import shutil
import streamlit as st

# Reset function
def reset():
	# Remove the source_files folder
	shutil.rmtree("source_files", ignore_errors=True)
	# Remove the output_files folder
	shutil.rmtree("output_files", ignore_errors=True)
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
	  
# Reset the web app
reset()
# Define the title of the web app
st.title("Multi-Day Outbound Efficiency Analysis")

# User input for the start and end date
start_date = st.date_input("Please Select the Start Date")
end_date = st.date_input("Please Select the End Date")
# Generate date range between start and end date
date_range = pd.date_range(start_date, end_date).date
# Initialize a dictionary to store the shift hours
shift_hours = {}
# User input for shift hours
for date in date_range:
	# User input for shift hours
	day_shift_hours = st.text_input(f"请输入 {date} 的白班总工时")
	night_shift_hours = st.text_input(f"请输入 {date} 的大夜班总工时")
	# Convert to float type
	day_shift_hours = float(day_shift_hours) if day_shift_hours else 0
	night_shift_hours = float(night_shift_hours) if night_shift_hours else 0
	# Add the shift hours to the dictionary
	shift_hours[f"{date}_白班"] = day_shift_hours
	shift_hours[f"{date}_大夜班"] = night_shift_hours
# Load the data and keep only the required columns
uploaded_file = st.file_uploader("Upload Outbound Report File", type=['xlsx'])
# Define source_files folder
source_files_folder = 'source_files'
# Create the directory if it doesn't exist
os.makedirs(source_files_folder, exist_ok=True)
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

if st.button("Process File"):
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

	# Convert the time columns to datetime format
	data['创建时间'] = pd.to_datetime(data['创建时间'], errors='coerce')
	data['汇波完成时间'] = pd.to_datetime(data['汇波完成时间'], errors='coerce')
	data['拣选完成时间'] = pd.to_datetime(data['拣选完成时间'], errors='coerce')
	data['复核完成时间'] = pd.to_datetime(data['复核完成时间'], errors='coerce')

	# Create date and hour columns based on the specified time columns
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
		if 21 <= hour <= 23:
			return f'{date + pd.Timedelta(days=1)}_大夜班'
		elif 0 <= hour < 6:
			return f'{date}_大夜班'
		elif 6 <= hour < 18:
			return f'{date}_白班'
		else:
			return f'{date}_Other'

	data['班次'] = data.apply(lambda row: determine_shift(row['复核日期'], row['复核小时']), axis=1)

	# Filter the data based on the selected date range
	start_datetime = pd.to_datetime(f"{start_date} 00:00") - pd.Timedelta(days=1)
	filtered_data = data[(data['复核完成时间'] >= start_datetime) & (data['复核完成时间'] <= pd.to_datetime(end_date) + pd.Timedelta(days=1))]

	# Calculate packing orders and items per hour
	hourly_summary = filtered_data.groupby(['班次', '复核小时']).agg(
		每小时复核打包单数=('出库单号', 'nunique'),
		每小时复核打包件数=('出库货品数量', 'sum')
	).reset_index()

	# Sum up the hourly summary to get the shift summary
	shift_summary = hourly_summary.groupby('班次').agg(
		复核打包完成单数=('每小时复核打包单数', 'sum'),
		复核打包完成件数=('每小时复核打包件数', 'sum'),
		平均每小时复核打包件数=('每小时复核打包件数', 'mean')
	).reset_index()

	# Add the total working hours for each shift
	shift_summary['总工时'] = shift_summary['班次'].apply(lambda x: shift_hours.get(x, 0))

	# Calculate packing efficiency
	shift_summary['件效'] = shift_summary.apply(lambda row: row['复核打包完成件数'] / row['总工时'] if row['总工时'] > 0 else 0, axis=1)

	# Make sure all shifts are included in the summary
	for date in date_range:
		for shift in ['白班', '大夜班', 'Other']:
			key = f"{date}_{shift}"
			if key not in shift_summary['班次'].values:
				new_row = {'班次': key, '复核打包完成单数': 0, '复核打包完成件数': 0, '平均每小时复核打包件数': 0, '总工时': 0, '件效': 0}
				shift_summary = pd.concat([shift_summary, pd.DataFrame([new_row])], ignore_index=True)

	# Calculate the daily summary
	shift_summary['班次日期'] = shift_summary['班次'].apply(lambda x: x.split('_')[0])
	daily_summary = shift_summary.groupby('班次日期').agg(
		复核打包完成单数=('复核打包完成单数', 'sum'),
		复核打包完成件数=('复核打包完成件数', 'sum'),
		总工时=('总工时', 'sum'),
		件效=('件效', 'mean')
	).reset_index()

	daily_summary['平均每小时复核打包件数'] = daily_summary['复核打包完成件数'] / daily_summary['总工时']

	# Calculate the overall summary
	overall_summary = shift_summary.groupby('班次').agg(
		复核打包完成单数=('复核打包完成单数', 'sum'),
		复核打包完成件数=('复核打包完成件数', 'sum'),
		总工时=('总工时', 'sum')
	).reset_index()

	overall_summary['件效'] = overall_summary.apply(lambda row: row['复核打包完成件数'] / row['总工时'] if row['总工时'] > 0 else 0, axis=1)
	overall_summary['平均每小时复核打包件数'] = overall_summary['复核打包完成件数'] / (overall_summary['总工时'] / len(overall_summary))

	# Calculate the total summary for the specified date range
	total_summary = pd.DataFrame({
		'开始日期': [start_date],
		'结束日期': [end_date],
		'复核打包完成单数': [shift_summary['复核打包完成单数'].sum()],
		'复核打包完成件数': [shift_summary['复核打包完成件数'].sum()],
		'总工时': [shift_summary['总工时'].sum()],
		'件效': [shift_summary['复核打包完成件数'].sum() / shift_summary['总工时'].sum()],
		'平均每小时复核打包件数': [shift_summary['复核打包完成件数'].sum() / shift_summary['总工时'].sum()]
	})
	# Drop rows with index containing 'Other'
	shift_summary = shift_summary[~shift_summary['班次'].str.contains('Other')]
	overall_summary = overall_summary[~overall_summary['班次'].str.contains('Other')]
	# Define output_files folder
	output_files_folder = 'output_files'
	# Create the directory if it doesn't exist
	os.makedirs(output_files_folder, exist_ok=True)
	# Define new file name
	new_filename = f"summary-result-{start_date}-to-{end_date}.xlsx"
	# Save the summary results to an Excel file
	output_file = f'{output_files_folder}/{new_filename}'
	with pd.ExcelWriter(output_file) as writer:
		hourly_summary.to_excel(writer, sheet_name='Hourly Summary', index=False)
		shift_summary.to_excel(writer, sheet_name='Shift Summary', index=False)
		daily_summary.to_excel(writer, sheet_name='Daily Summary', index=False)
		overall_summary.to_excel(writer, sheet_name='Overall Summary', index=False)
		total_summary.to_excel(writer, sheet_name='Total Summary', index=False)

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
	st.write("Hourly Summary")
	st.write(hourly_summary)
	st.write("Shift Summary")
	st.write(shift_summary)
	st.write("Daily Summary")
	st.write(daily_summary)
	st.write("Overall Summary")
	st.write(overall_summary)
	st.write("Total Summary")
	st.write(total_summary)
