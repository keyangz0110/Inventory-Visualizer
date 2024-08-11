import pandas as pd
import os
import threading
import re
import shutil
import uuid
import time
import random
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
		raise FileNotFoundError("No file starting with '人员名单' found in the specified folder.")

# Define the title of the web app
st.title("Worker Schedule Generator")
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
uploaded_file = st.file_uploader("Upload Name List", type=['xlsx'])
# Create radio buttons for selecting the report type
selection = st.radio("Select Type", ["入库", "出库"], horizontal=True)
# Create text inputs for entering the data
if selection == "入库":
	mon_putaway = st.text_input("请输入周一上架数量")
	tue_putaway = st.text_input("请输入周二上架数量")
	wed_putaway = st.text_input("请输入周三上架数量")
	thu_putaway = st.text_input("请输入周四上架数量")
	fri_putaway = st.text_input("请输入周五上架数量")
	sat_putaway = st.text_input("请输入周六上架数量")
	sun_putaway = st.text_input("请输入周日上架数量")
	weekly_avg_separating = st.text_input("请输入周平均分货效率")
	weekly_avg_receiving = st.text_input("请输入周平均收货效率")
	weekly_avg_putaway = st.text_input("请输入周平均上架效率")
elif selection == "出库":
	mon_ob_amount = st.text_input("请输入周一出库单量")
	tue_ob_amount = st.text_input("请输入周二出库单量")
	wed_ob_amount = st.text_input("请输入周三出库单量")
	thu_ob_amount = st.text_input("请输入周四出库单量")
	fri_ob_amount = st.text_input("请输入周五出库单量")
	sat_ob_amount = st.text_input("请输入周六出库单量")
	sun_ob_amount = st.text_input("请输入周日出库单量")
	weekly_avg_picking = st.text_input("请输入周平均拣货效率")
	weekly_avg_printing = st.text_input("请输入周平均复核效率")
	weekly_avg_packing = st.text_input("请输入周平均打包效率")
	weekly_avg_gaylord = st.text_input("请输入周平均组大包效率")
else:
	raise ValueError("Invalid selection.")
# Start remove directory timer
remove_directory_thread(source_files_folder)
# Save the uploaded files to the source_files folder
if uploaded_file:
	with open(os.path.join(source_files_folder, uploaded_file.name), "wb") as f:
		f.write(uploaded_file.getbuffer())
# List all files in the directory
all_files = os.listdir(source_files_folder)
# Define the regular expression pattern
uploaded_file_pattern = re.compile(r'^人员名单.*\.xlsx$')
# Filter files that match the pattern
uploaded_file_matching_files = [f for f in all_files if uploaded_file_pattern.match(f)]

if st.button("Generate"):
	# Read the files
	read_files()
	# Convert the input values to integers
	mon_ob_amount = int(mon_ob_amount)
	tue_ob_amount = int(tue_ob_amount)
	wed_ob_amount = int(wed_ob_amount)
	thu_ob_amount = int(thu_ob_amount)
	fri_ob_amount = int(fri_ob_amount)
	sat_ob_amount = int(sat_ob_amount)
	sun_ob_amount = int(sun_ob_amount)
	weekly_avg_picking = int(weekly_avg_picking)
	weekly_avg_printing = int(weekly_avg_printing)
	weekly_avg_packing = int(weekly_avg_packing)
	weekly_avg_gaylord = int(weekly_avg_gaylord)
	# if the selection is outbound
	if selection == '出库':
		# Extract the first column as picking category
		picking = uploaded_file.iloc[:, 0]
		# Extract the second column as printing category
		printing = uploaded_file.iloc[:, 1]
		# Extract the second column as packing category
		packing = uploaded_file.iloc[:, 2]
		# Extract the third column as gaylord category
		gaylord = uploaded_file.iloc[:, 3]
		# Convert the picking category to a set and a list
		picking_set = set(picking)
		picking_list = list(picking_set)
		# Convert the printing category to a set and a list
		printing_set = set(printing)
		printing_list = list(printing_set)
		# Convert the packing category to a set and a list
		packing_set = set(packing)
		packing_list = list(packing_set)
		# Convert the gaylord category to a set and a list
		gaylord_set = set(gaylord)
		gaylord_list = list(gaylord_set)
		# Create a dictionary to store the picking category
		picking_count = {element: 0 for element in picking_set}
		# Create a dictionary to store the printing category
		printing_count = {element: 0 for element in printing_set}
		# Create a dictionary to store the packing category
		packing_count = {element: 0 for element in packing_set}
		# Create a dictionary to store the gaylord category
		gaylord_count = {element: 0 for element in gaylord_set}
		# Calculate daily picking worker amount
		mon_picking = mon_ob_amount // weekly_avg_picking // 8
		tue_picking = tue_ob_amount // weekly_avg_picking // 8
		wed_picking = wed_ob_amount // weekly_avg_picking // 8
		thu_picking = thu_ob_amount // weekly_avg_picking // 8
		fri_picking = fri_ob_amount // weekly_avg_picking // 8
		sat_picking = sat_ob_amount // weekly_avg_picking // 8
		sun_picking = sun_ob_amount // weekly_avg_picking // 8
		# Calculate daily printing worker amount
		mon_printing = mon_ob_amount // weekly_avg_printing // 8
		tue_printing = tue_ob_amount // weekly_avg_printing // 8
		wed_printing = wed_ob_amount // weekly_avg_printing // 8
		thu_printing = thu_ob_amount // weekly_avg_printing // 8
		fri_printing = fri_ob_amount // weekly_avg_printing // 8
		sat_printing = sat_ob_amount // weekly_avg_printing // 8
		sun_printing = sun_ob_amount // weekly_avg_printing // 8
		# Calculate daily packing worker amount
		mon_packing = mon_ob_amount // weekly_avg_packing // 8
		tue_packing = tue_ob_amount // weekly_avg_packing // 8
		wed_packing = wed_ob_amount // weekly_avg_packing // 8
		thu_packing = thu_ob_amount // weekly_avg_packing // 8
		fri_packing = fri_ob_amount // weekly_avg_packing // 8
		sat_packing = sat_ob_amount // weekly_avg_packing // 8
		sun_packing = sun_ob_amount // weekly_avg_packing // 8
		# Calculate daily gaylord worker amount
		mon_gaylord = mon_ob_amount // weekly_avg_gaylord // 8
		tue_gaylord = tue_ob_amount // weekly_avg_gaylord // 8
		wed_gaylord = wed_ob_amount // weekly_avg_gaylord // 8
		thu_gaylord = thu_ob_amount // weekly_avg_gaylord // 8
		fri_gaylord = fri_ob_amount // weekly_avg_gaylord // 8
		sat_gaylord = sat_ob_amount // weekly_avg_gaylord // 8
		sun_gaylord = sun_ob_amount // weekly_avg_gaylord // 8
		# Dictionary mapping days to their respective picking values
		picking_values = {
			'mon': mon_picking,
			'tue': tue_picking,
			'wed': wed_picking,
			'thu': thu_picking,
			'fri': fri_picking,
			'sat': sat_picking,
			'sun': sun_picking
		}
		# Dictionary mapping days to their respective printing values
		printing_values = {
			'mon': mon_printing,
			'tue': tue_printing,
			'wed': wed_printing,
			'thu': thu_printing,
			'fri': fri_printing,
			'sat': sat_printing,
			'sun': sun_printing
		}
		# Dictionary mapping days to their respective packing values
		packing_values = {
			'mon': mon_packing,
			'tue': tue_packing,
			'wed': wed_packing,
			'thu': thu_packing,
			'fri': fri_packing,
			'sat': sat_packing,
			'sun': sun_packing
		}
		# Dictionary mapping days to their respective gaylord values
		gaylord_values = {
			'mon': mon_gaylord,
			'tue': tue_gaylord,
			'wed': wed_gaylord,
			'thu': thu_gaylord,
			'fri': fri_gaylord,
			'sat': sat_gaylord,
			'sun': sun_gaylord
		}
		# Initialize dictionaries to store selected workers for each day
		selected_workers = {
			'mon': {'Picking': [], 'Printing': [], 'Packing': [], 'Gaylord': []},
			'tue': {'Picking': [], 'Printing': [], 'Packing': [], 'Gaylord': []},
			'wed': {'Picking': [], 'Printing': [], 'Packing': [], 'Gaylord': []},
			'thu': {'Picking': [], 'Printing': [], 'Packing': [], 'Gaylord': []},
			'fri': {'Picking': [], 'Printing': [], 'Packing': [], 'Gaylord': []},
			'sat': {'Picking': [], 'Printing': [], 'Packing': [], 'Gaylord': []},
			'sun': {'Picking': [], 'Printing': [], 'Packing': [], 'Gaylord': []}
		}

		# Select picking workers for each day
		for day, picking_value in picking_values.items():
			# Filter the picking category with less than 5
			available_picking = [element for element in picking_list if picking_count[element] < 5]
			# Break the loop if no available picking category is found
			if not available_picking:
				break
			# Ensure we do not select more workers than available
			if len(available_picking) < picking_value:
				picking_value = len(available_picking)
			# Select workers randomly based on the daily worker amount
			selected_picking_workers = random.sample(available_picking, k=picking_value)
			# Update the picking count
			for worker in selected_picking_workers:
				picking_count[worker] += 1
			# Store the selected workers for the day
			selected_workers[day]['Picking'] = selected_picking_workers
		# Select printing workers for each day
		for day, printing_value in printing_values.items():
			# Filter the printing category with less than 5
			available_printing = [element for element in printing_list if printing_count[element] < 5]
			# Break the loop if no available printing category is found
			if not available_printing:
				break
			# Ensure we do not select more workers than available
			if len(available_printing) < printing_value:
				printing_value = len(available_printing)
			# Select workers randomly based on the daily worker amount
			selected_printing_workers = random.sample(available_printing, k=printing_value)
			# Update the printing count
			for worker in selected_printing_workers:
				printing_count[worker] += 1
			# Store the selected workers for the day
			selected_workers[day]['Printing'] = selected_printing_workers
		# Select packing workers for each day
		for day, packing_value in packing_values.items():
			# Filter the packing category with less than 5
			available_packing = [element for element in packing_list if packing_count[element] < 5]
			# Break the loop if no available packing category is found
			if not available_packing:
				break
			# Ensure we do not select more workers than available
			if len(available_packing) < packing_value:
				packing_value = len(available_packing)
			# Select workers randomly based on the daily worker amount
			selected_packing_workers = random.sample(available_packing, k=packing_value)
			# Update the packing count
			for worker in selected_packing_workers:
				packing_count[worker] += 1
			# Store the selected workers for the day
			selected_workers[day]['Packing'] = selected_packing_workers
		# Select gaylord workers for each day
		for day, gaylord_value in gaylord_values.items():
			# Filter the gaylord category with less than 5
			available_gaylord = [element for element in gaylord_list if gaylord_count[element] < 5]
			# Break the loop if no available gaylord category is found
			if not available_gaylord:
				break
			# Ensure we do not select more workers than available
			if len(available_gaylord) < gaylord_value:
				gaylord_value = len(available_gaylord)
			# Select workers randomly based on the daily worker amount
			selected_gaylord_workers = random.sample(available_gaylord, k=gaylord_value)
			# Update the gaylord count
			for worker in selected_gaylord_workers:
				gaylord_count[worker] += 1
			# Store the selected workers for the day
			selected_workers[day]['Gaylord'] = selected_gaylord_workers
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
		# Define file name
		filename = 'Generated-Schedule.xlsx'
		# Store the selected picking, packing, and gaylord workers to a new dataframe
		# Save the summary results to an Excel file
		output_file = f'{output_files_folder}//{filename}'
		with pd.ExcelWriter(output_file) as writer:
			for day in selected_workers:
				# Find the maximum length among all lists for the day
				max_length = max(len(selected_workers[day]['Picking']), len(selected_workers[day]['Printing']), len(selected_workers[day]['Packing']), len(selected_workers[day]['Gaylord']))
				# Pad each list with None values to match the maximum length
				selected_workers[day]['Picking'] += [None] * (max_length - len(selected_workers[day]['Picking']))
				selected_workers[day]['Printing'] += [None] * (max_length - len(selected_workers[day]['Printing']))
				selected_workers[day]['Packing'] += [None] * (max_length - len(selected_workers[day]['Packing']))
				selected_workers[day]['Gaylord'] += [None] * (max_length - len(selected_workers[day]['Gaylord']))
				print(selected_workers[day]['Picking'])
				# Create a DataFrame for the day
				df = pd.DataFrame(selected_workers[day])
				# Drop the None values
				df = df.dropna()
				# Write the DataFrame to a specific sheet
				df.to_excel(writer, sheet_name=day.capitalize(), index=False)
		# Display the table
		st.dataframe(df)
		# Provide a download button for the saved file
		with open(os.path.join(output_files_folder, filename), "rb") as file:
			btn = st.download_button(
				label="Download Generated Schedule",
				data=file,
				file_name=filename,
				mime="application//vnd.openxmlformats-officedocument.spreadsheetml.sheet"
			)
	elif selection == '入库':
		# Extract the first column as separating category
		separating = uploaded_file.iloc[:, 0]
		# Extract the second column as receiving category
		receiving = uploaded_file.iloc[:, 1]
		# Extract the third column as putaway category
		putaway = uploaded_file.iloc[:, 2]
		# Convert the separating category to a set and a list
		separating_set = set(separating)
		separating_list = list(separating_set)
		# Convert the receiving category to a set and a list
		receiving_set = set(receiving)
		receiving_list = list(receiving_set)
		# Convert the putaway category to a set and a list
		putaway_set = set(putaway)
		putaway_list = list(putaway_set)
		# Create a dictionary to store the separating category
		separating_count = {element: 0 for element in separating_set}
		# Create a dictionary to store the receiving category
		receiving_count = {element: 0 for element in receiving_set}
		# Create a dictionary to store the putaway category
		putaway_count = {element: 0 for element in putaway_set}
		# Calculate daily separating worker amount
		mon_separating = mon_putaway // weekly_avg_separating
		tue_separating = tue_putaway // weekly_avg_separating
		wed_separating = wed_putaway // weekly_avg_separating
		thu_separating = thu_putaway // weekly_avg_separating
		fri_separating = fri_putaway // weekly_avg_separating
		sat_separating = sat_putaway // weekly_avg_separating
		sun_separating = sun_putaway // weekly_avg_separating
		# Calculate daily receiving worker amount
		mon_receiving = mon_putaway // weekly_avg_receiving
		tue_receiving = tue_putaway // weekly_avg_receiving
		wed_receiving = wed_putaway // weekly_avg_receiving
		thu_receiving = thu_putaway // weekly_avg_receiving
		fri_receiving = fri_putaway // weekly_avg_receiving
		sat_receiving = sat_putaway // weekly_avg_receiving
		sun_receiving = sun_putaway // weekly_avg_receiving
		# Calculate daily putaway worker amount
		mon_putaway = mon_putaway // weekly_avg_putaway
		tue_putaway = tue_putaway // weekly_avg_putaway
		wed_putaway = wed_putaway // weekly_avg_putaway
		thu_putaway = thu_putaway // weekly_avg_putaway
		fri_putaway = fri_putaway // weekly_avg_putaway
		sat_putaway = sat_putaway // weekly_avg_putaway
		sun_putaway = sun_putaway // weekly_avg_putaway
		# Dictionary mapping days to their respective separating values
		separating_values = {
			'mon': mon_separating,
			'tue': tue_separating,
			'wed': wed_separating,
			'thu': thu_separating,
			'fri': fri_separating,
			'sat': sat_separating,
			'sun': sun_separating
		}
		# Dictionary mapping days to their respective receiving values
		receiving_values = {
			'mon': mon_receiving,
			'tue': tue_receiving,
			'wed': wed_receiving,
			'thu': thu_receiving,
			'fri': fri_receiving,
			'sat': sat_receiving,
			'sun': sun_receiving
		}
		# Dictionary mapping days to their respective putaway values
		putaway_values = {
			'mon': mon_putaway,
			'tue': tue_putaway,
			'wed': wed_putaway,
			'thu': thu_putaway,
			'fri': fri_putaway,
			'sat': sat_putaway,
			'sun': sun_putaway
		}
		# Select separating workers for each day
		for day, separating_value in separating_values.items():
			# Filter the separating category with less than 5
			available_separating = [element for element in separating_list if separating_count[element] < 5]
			# Break the loop if no available separating category is found
			if not available_separating:
				break
			# Select workers randomly based on the daily worker amount
			selected_separating_workers = random.choices(available_separating, k=separating_value[day])
			# Update the separating count
			separating_count[selected_separating_workers] += 1
		# Select receiving workers for each day
		for day, receiving_value in receiving_values.items():
			# Filter the receiving category with less than 5
			available_receiving = [element for element in receiving_list if receiving_count[element] < 5]
			# Break the loop if no available receiving category is found
			if not available_receiving:
				break
			# Select workers randomly based on the daily worker amount
			selected_receiving_workers = random.choices(available_receiving, k=receiving_value[day])
			# Update the receiving count
			receiving_count[selected_receiving_workers] += 1
		# Select putaway workers for each day
		for day, putaway_value in putaway_values.items():
			# Filter the putaway category with less than 5
			available_putaway = [element for element in putaway_list if putaway_count[element] < 5]
			# Break the loop if no available putaway category is found
			if not available_putaway:
				break
			# Select workers randomly based on the daily worker amount
			selected_putaway_workers = random.choices(available_putaway, k=putaway_value[day])
			# Update the putaway count
			putaway_count[selected_putaway_workers] += 1
