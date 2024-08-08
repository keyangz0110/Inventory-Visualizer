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
	st.text_input("请输入周一上架数量")
	st.text_input("请输入周二上架数量")
	st.text_input("请输入周三上架数量")
	st.text_input("请输入周四上架数量")
	st.text_input("请输入周五上架数量")
	st.text_input("请输入周六上架数量")
	st.text_input("请输入周日上架数量")
elif selection == "出库":
	st.text_input("请输入周一出库单量")
	st.text_input("请输入周二出库单量")
	st.text_input("请输入周三出库单量")
	st.text_input("请输入周四出库单量")
	st.text_input("请输入周五出库单量")
	st.text_input("请输入周六出库单量")
	st.text_input("请输入周日出库单量")
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
