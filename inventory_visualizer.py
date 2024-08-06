import pandas as pd
import numpy as np
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

def read_files():
	# Declare the global variables
	global goods_info, outbound_info, weekly_inventory, inventory
	# Check if any matching files are found
	if goods_info_matching_files:
		# Construct the full path of the first matching file
		goods_info_file_path = os.path.join(source_files_folder, goods_info_matching_files[0])
		# Read the first matching file
		goods_info = pd.read_excel(goods_info_file_path)
		# Convert the "货品编码" column to string type
		goods_info["货品编码"] = goods_info["货品编码"].astype(str)
	else:
		raise FileNotFoundError("No file starting with '货品' found in the specified folder.")
	if ob_info_matching_files:
		# Construct the full path of the first matching file
		ob_info_file_path = os.path.join(source_files_folder, ob_info_matching_files[0])
		# Read the first matching file
		outbound_info = pd.read_excel(ob_info_file_path)
		# Convert the "货品编码" column to string type
		outbound_info["货品编码"] = outbound_info["货品编码"].astype(str)
	else:
		raise FileNotFoundError("No file starting with '出库单报表' found in the specified folder.")
	if weekly_inventory_matching_files:
		# Construct the full path of the first matching file
		weekly_inventory_file_path = os.path.join(source_files_folder, weekly_inventory_matching_files[0])
		# Read the first matching file
		weekly_inventory = pd.read_excel(weekly_inventory_file_path)
		# Convert the "货品编码" column to string type
		weekly_inventory["货品编码"] = weekly_inventory["货品编码"].astype(str)
	else:
		raise FileNotFoundError("No file starting with '库存快照报' found in the specified folder.")
	if inventory_matching_files:
		# Construct the full path of the first matching file
		inventory_file_path = os.path.join(source_files_folder, inventory_matching_files[0])
		# Read the first matching file
		inventory = pd.read_excel(inventory_file_path)
		# Convert the "货品编码" column to string type
		inventory["货品编码"] = inventory["货品编码"].astype(str)
	else:
		raise FileNotFoundError("No file starting with '库存明细' found in the specified folder.")

# Set the page configuration
# st.set_page_config(page_title="Inventory Visualizer",
				   # page_icon=":bar_chart:",
				   # layout="centered")
# Reset the web app
# reset()
# Define the title of the web app
st.title("Inventory Visualizer")
# Generate a unique identifier for the session
session_id = str(uuid.uuid4())
# File uploader
goods_report_file = st.file_uploader("Upload Goods Report", type=["xlsx"])
ob_report_file = st.file_uploader("Upload Outbound Report", type=["xlsx"])
weekly_inventory_file = st.file_uploader("Upload Weekly Inventory Report", type=["xlsx"])
inventory_file = st.file_uploader("Upload Inventory Report", type=["xlsx"])
# Create three radio buttons
selection = st.radio("Select Desired Report", ["动销", "移位建议", "Selection 3"], horizontal=True)
# Define source_files folder
source_files_folder = f'source_files_{session_id}'
# Create the directory if it doesn't exist
os.makedirs(source_files_folder, exist_ok=True)
# Start remove directory timer
remove_directory(source_files_folder)
# Save the uploaded files to the source_files folder
if goods_report_file:
	with open(os.path.join(source_files_folder, goods_report_file.name), "wb") as f:
		f.write(goods_report_file.getbuffer())
if ob_report_file:
	with open(os.path.join(source_files_folder, ob_report_file.name), "wb") as f:
		f.write(ob_report_file.getbuffer())
if weekly_inventory_file:
	with open(os.path.join(source_files_folder, weekly_inventory_file.name), "wb") as f:
		f.write(weekly_inventory_file.getbuffer())
if inventory_file:
	with open(os.path.join(source_files_folder, inventory_file.name), "wb") as f:
		f.write(inventory_file.getbuffer())
# List all files in the directory
all_files = os.listdir(source_files_folder)
# Define the regular expression pattern
goods_info_file_pattern = re.compile(r'^货品.*\.xlsx$')
ob_info_file_pattern = re.compile(r'^出库单报表.*\.xlsx$')
weekly_inventory_file_pattern = re.compile(r'^库存快照报.*\.xlsx$')
inventory_file_pattern = re.compile(r'^库存明细.*\.xlsx$')
# Filter files that match the pattern
goods_info_matching_files = [f for f in all_files if goods_info_file_pattern.match(f)]
ob_info_matching_files = [f for f in all_files if ob_info_file_pattern.match(f)]
weekly_inventory_matching_files = [f for f in all_files if weekly_inventory_file_pattern.match(f)]
inventory_matching_files = [f for f in all_files if inventory_file_pattern.match(f)]

if st.button("Process Files"):
	# Check if any matching files are found
	read_files()
	# For goods info, trim the columns, only keep columns with indices of names "货品编码", "长", "宽", "高", "重量"
	goods_info_trimmed = goods_info[["货品编码", "长", "宽", "高", "重量"]].groupby("货品编码").first()
	# Remove rows that have empty "长", "宽", "高", "重量"
	goods_info_trimmed = goods_info_trimmed.dropna(subset=["长", "宽", "高", "重量"])
	# Slice "in" at the end of "长", "宽", and "高" columns for each "货品编码"
	goods_info_trimmed["长"] = goods_info_trimmed["长"].astype(str).apply(lambda x: str(x[:-2]))
	goods_info_trimmed["宽"] = goods_info_trimmed["宽"].astype(str).apply(lambda x: str(x[:-2]))
	goods_info_trimmed["高"] = goods_info_trimmed["高"].astype(str).apply(lambda x: str(x[:-2]))
	# Remove "lb" at the end of "重量" column for each "货品编码"
	goods_info_trimmed["重量"] = goods_info_trimmed["重量"].astype(str).apply(lambda x: str(x[:-2]))
	# Calculate the volume of each item
	goods_info_trimmed["体积"] = goods_info_trimmed["长"].astype(float) * goods_info_trimmed["宽"].astype(float) * goods_info_trimmed["高"].astype(float)
	# Limit the decimal places to 2
	goods_info_trimmed["体积"] = goods_info_trimmed["体积"].apply(lambda x: round(x, 2))
	# For outbound info, trim the columns, only keep columns with indices of names "货品编码" and "出库货品数量"
	outbound_info_trimmed = outbound_info[["外部单号", "物流运单号", "拣选单号", "出库单状态", "货品编码", "出库货品数量", "货品的长", "货品的宽", "货品的高"]]
	# For outbound info, remove rows with "出库单状态" equal to "已取消"
	outbound_info_trimmed = outbound_info_trimmed[outbound_info_trimmed["出库单状态"] != "已取消"]
	# For weekly inventory, trim the columns, only keep columns with indices of names "货品编码" and "库位库存"
	weekly_inventory_trimmed = weekly_inventory[["货品编码", "库位库存"]]
	# For inventory, trim the columns, only keep columns with indices of names "库位编码", "货品编码" and "总库存"
	inventory_trimmed = inventory[["库位编码", "货品编码", "总库存"]]
	# For outbound info, use "货品编码" as the key, sum up the "出库货品数量" for each unique "货品编码"
	outbound_info_grouped = outbound_info_trimmed.groupby("货品编码").sum()
	# Calculate the average of total outbound quantity for each unique "货品编码"
	outbound_info_grouped["平均每天出库量"] = outbound_info_grouped["出库货品数量"] / 7
	# Limit the decimal places to 2
	outbound_info_grouped["平均每天出库量"] = outbound_info_grouped["平均每天出库量"].apply(lambda x: round(x, 2))
	# Use "货品编码" as the key, find all "外部单号" for each unique "货品编码"
	outbound_info_grouped["外部单号"] = outbound_info_trimmed.groupby("货品编码")["外部单号"].apply(list)
	# Remove duplicate "外部单号" for each unique "货品编码"
	outbound_info_grouped["外部单号"] = outbound_info_grouped["外部单号"].apply(lambda x: list(set(x)))
	# Sort the "外部单号" for each unique "货品编码" alphabetically
	outbound_info_grouped["外部单号"] = outbound_info_grouped["外部单号"].apply(lambda x: sorted(x))
	# Use "货品编码" as the key, find all "物流运单号" for each unique "货品编码"
	outbound_info_grouped["物流运单号"] = outbound_info_trimmed.groupby("货品编码")["物流运单号"].apply(list)
	# Remove duplicate "物流运单号" for each unique "货品编码"
	outbound_info_grouped["物流运单号"] = outbound_info_grouped["物流运单号"].apply(lambda x: list(set(x)))
	# Sort the "物流运单号" for each unique "货品编码" alphabetically
	# outbound_info_grouped["物流运单号"] = outbound_info_grouped["物流运单号"].apply(lambda x: sorted(x))
	# Use "货品编码" as the key, find all "拣选单号" for each unique "货品编码"
	outbound_info_grouped["拣选单号"] = outbound_info_trimmed.groupby("货品编码")["拣选单号"].apply(list)
	# Remove duplicate "拣选单号" for each unique "货品编码"
	outbound_info_grouped["拣选单号"] = outbound_info_grouped["拣选单号"].apply(lambda x: list(set(x)))
	# Sort the "拣选单号" for each unique "货品编码" alphabetically
	# outbound_info_grouped["拣选单号"] = outbound_info_grouped["拣选单号"].apply(lambda x: sorted(x))
	# Use "货品编码" as the key, find all "出库单状态" for each unique "货品编码"
	outbound_info_grouped["出库单状态"] = outbound_info_trimmed.groupby("货品编码")["出库单状态"].apply(list)
	# Remove duplicate "出库单状态" for each unique "货品编码"
	outbound_info_grouped["出库单状态"] = outbound_info_grouped["出库单状态"].apply(lambda x: list(set(x)))
	# Sort the "出库单状态" for each unique "货品编码" alphabetically
	outbound_info_grouped["出库单状态"] = outbound_info_grouped["出库单状态"].apply(lambda x: sorted(x))
	# For weekly inventory, use "货品编码" as the key, sum up the "库位库存" for each unique "货品编码"
	weekly_inventory_grouped = weekly_inventory_trimmed.groupby("货品编码").sum()
	# Calculate average of weekly total inventory for each unique "货品编码"
	weekly_inventory_grouped["平均每天库存量"] = weekly_inventory_grouped["库位库存"] / 7
	# Limit the decimal places to 2
	weekly_inventory_grouped["平均每天库存量"] = weekly_inventory_grouped["平均每天库存量"].apply(lambda x: round(x, 2))
	# For inventory, use "货品编码" as the key, sum up the "库位库存" for each unique "货品编码"
	inventory_grouped = inventory_trimmed.groupby("货品编码").sum()
	# Use "货品编码" as the key, find all "库位编码" for each unique "货品编码"
	inventory_grouped["库位编码"] = inventory_trimmed.groupby("货品编码")["库位编码"].apply(list)
	# Remove duplicate "库位编码" for each unique "货品编码"
	inventory_grouped["库位编码"] = inventory_grouped["库位编码"].apply(lambda x: list(set(x)))
	# Remove strings start with "DMG" and end with "ZCW" in "库位编码" for each unique "货品编码"
	inventory_grouped["库位编码"] = inventory_grouped["库位编码"].apply(lambda x: [i for i in x if not i.startswith("DMG") and not i.endswith("ZCW")])
	# Sort the "库位编码" for each unique "货品编码" alphabetically
	inventory_grouped["库位编码"] = inventory_grouped["库位编码"].apply(lambda x: sorted(x))
	# Count the number of unique "库位编码" for each unique "货品编码"
	inventory_grouped["库位数量"] = inventory_grouped["库位编码"].apply(len)
	# Use "货品编码" as the key, merge three dataframes
	result = pd.merge(inventory_grouped, goods_info_trimmed, how="left", on="货品编码")
	result = pd.merge(result, weekly_inventory_grouped, how="left", on="货品编码")
	result = pd.merge(result, outbound_info_grouped, how="left", on="货品编码")
	# Calculate outbound ratio
	result["出库比例"] = result["平均每天出库量"] / result["平均每天库存量"]
	# Calculate days sales of inventory
	result["周转天数"] = result["平均每天库存量"] / result["平均每天出库量"]
	# Limit the decimal places to 2
	result["周转天数"] = result["周转天数"].apply(lambda x: round(x, 2))
	# Calculate the total inventory volume of each item
	result["总库存体积"] = result["体积"] * result["总库存"]
	# Calculate the total outbound volume of each item
	result["总出库体积"] = result["体积"] * result["出库货品数量"]
	# Calculate rank of a product based on days sales of inventory
	# If one product has no outbound record, put it in G rank
	conditions = [
		(result["周转天数"] < 1),
		(result["周转天数"] >= 1) & (result["周转天数"] < 10),
		(result["周转天数"] >= 10) & (result["周转天数"] < 100),
		(result["周转天数"] >= 100) & (result["周转天数"] < 1000),
		(result["周转天数"] >= 1000),
		(result["周转天数"].isnull())
	]
	# Define corresponding values for 动销等级
	choices = ["B", "C", "D", "E", "F", "G"]
	# Apply conditions to create 动销等级 column
	result["动销等级"] = np.select(conditions, choices, default="N/A")
	# If the user selects "动销" and clicks the "Process Files" button
	if selection == "动销":
		# Only keep rows that "出库比例" is not NaN, infinity, and 0
		# result = result[(result["出库比例"].notnull()) & (result["出库比例"] != float("inf")) & (result["出库比例"] != 0)]
		# Sort the result by "动销等级" in descending order
		result = result.sort_values(by="动销等级", ascending=False)
		# Limit the decimal places to 2
		result["出库比例"] = result["出库比例"].apply(lambda x: round(x, 2))
		# print the result with only "库位编码", "总库存", "出库货品数量", "出库比例" columns
		st.write(result[["库位编码", "库位数量", "总库存", "平均每天库存量", "出库货品数量", "平均每天出库量", "出库比例", "周转天数", "体积", "总库存体积", "总出库体积", "动销等级"]])
	# If the user selects "Selection 2" and clicks the "Process Files" button
	elif selection == "移位建议":
		# For ranks that are "E", "F", and "G" from column "动销等级", if the product exists in both X and Y sections from "库位编码",
		# select one section from X and Y randomly, and remove the other sections, put it in the "移位建议" column.
		if "动销等级" in result.columns:
			# Select the rows that have "动销等级" of "E", "F", and "G"
			rank_e = result[result["动销等级"] == "E"]
			rank_f = result[result["动销等级"] == "F"]
			rank_g = result[result["动销等级"] == "G"]
			# Initialize the "移位建议" column with empty strings
			result["移位建议"] = ""
			# To determine if the product exists in X or Y sections, check if "X" or "Y" letters are in the "库位编码" column.
			# If the set contains elements start with "X" or "Y", select the first occurrence of "X" or "Y" and put it in the "移位建议" column.
			# For each row in "库位编码" column, if the product exists in X or Y sections,
			# select the first section occurrence from either X or Y, put it in the "移位建议" column.
			for idx, row in rank_e.iterrows():
				location_list = row["库位编码"]
				if isinstance(location_list, list):
					for location in location_list:
						if "X" in location:
							result.at[idx, "移位建议"] = location
							break
						elif "Y" in location:
							result.at[idx, "移位建议"] = location
							break
			for idx, row in rank_f.iterrows():
				location_list = row["库位编码"]
				if isinstance(location_list, list):
					for location in location_list:
						if "X" in location:
							result.at[idx, "移位建议"] = location
							break
						elif "Y" in location:
							result.at[idx, "移位建议"] = location
							break
			for idx, row in rank_g.iterrows():
				location_list = row["库位编码"]
				if isinstance(location_list, list):
					for location in location_list:
						if "X" in location:
							result.at[idx, "移位建议"] = location
							break
						elif "Y" in location:
							result.at[idx, "移位建议"] = location
							break
			# Select the rows that have "动销等级" of "B", "C", and "D"
			rank_b = result[result["动销等级"] == "B"]
			rank_c = result[result["动销等级"] == "C"]
			rank_d = result[result["动销等级"] == "D"]

			for idx, row in rank_b.iterrows():
				location_list = row["库位编码"]
				if isinstance(location_list, list):
					for location in location_list:
						if "S1" in location or "S2" in location:
							result.at[idx, "移位建议"] = "K, M, N, X, Y"
							break
			for idx, row in rank_c.iterrows():
				location_list = row["库位编码"]
				if isinstance(location_list, list):
					for location in location_list:
						if "S1" in location or "S2" in location:
							result.at[idx, "移位建议"] = "K, M, N, X, Y"
							break
			for idx, row in rank_d.iterrows():
				location_list = row["库位编码"]
				if isinstance(location_list, list):
					for location in location_list:
						if "S1" in location or "S2" in location:
							result.at[idx, "移位建议"] = "K, M, N, X, Y"
							break
		# print the result with only "库位编码", "总库存", "出库货品数量", "出库比例" columns
		st.write(result[["库位编码", "库位数量", "总库存", "动销等级", "移位建议"]])
