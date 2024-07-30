import pandas as pd
import numpy as np
import os
import re
import shutil
import streamlit as st

# Reset function
def reset():
	# Remove the source_files folder
	shutil.rmtree("source_files", ignore_errors=True)

# Set the page configuration
st.set_page_config(page_title="Inventory Visualizer",
				   page_icon=":bar_chart:",
				   layout="centered")
# Reset the web app
reset()
# Define the title of the web app
st.title("Inventory Visualizer")
# File uploader
ob_report_file = st.file_uploader("Upload Outbound Report", type=["xlsx"])
weekly_inventory_file = st.file_uploader("Upload Weekly Inventory Report", type=["xlsx"])
inventory_file = st.file_uploader("Upload Inventory Report", type=["xlsx"])
# Define source_files folder
source_files_folder = 'source_files'
# Create the directory if it doesn't exist
os.makedirs(source_files_folder, exist_ok=True)
# Save the uploaded files to the source_files folder
if ob_report_file:
	with open(os.path.join(source_files_folder, ob_report_file.name), "wb") as f:
		f.write(ob_report_file.getbuffer())
if weekly_inventory_file:
	with open(os.path.join(source_files_folder, weekly_inventory_file.name), "wb") as f:
		f.write(weekly_inventory_file.getbuffer())
if inventory_file:
	with open(os.path.join(source_files_folder, inventory_file.name), "wb") as f:
		f.write(inventory_file.getbuffer())
if st.button("Process Files"):
	# List all files in the directory
	all_files = os.listdir(source_files_folder)
	# Define the regular expression pattern
	ob_info_file_pattern = re.compile(r'^出库单报表.*\.xlsx$')
	weekly_inventory_file_pattern = re.compile(r'^库存快照报.*\.xlsx$')
	inventory_file_pattern = re.compile(r'^库存明细.*\.xlsx$')
	# Filter files that match the pattern
	ob_info_matching_files = [f for f in all_files if ob_info_file_pattern.match(f)]
	weekly_inventory_matching_files = [f for f in all_files if weekly_inventory_file_pattern.match(f)]
	inventory_matching_files = [f for f in all_files if inventory_file_pattern.match(f)]
	# Check if any matching files are found
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

	# For outbound info, trim the columns, only keep columns with indices of names "货品编码" and "出库货品数量"
	outbound_info_trimmed = outbound_info[["外部单号", "物流运单号", "拣选单号", "出库单状态", "货品编码", "出库货品数量", "货品的长", "货品的宽", "货品的高"]]
	# For outbound info, remove rows with "出库单状态" equal to "已取消"
	outbound_info_trimmed = outbound_info_trimmed[outbound_info_trimmed["出库单状态"] != "已取消"]
	# Calculate the volume of each item
	outbound_info_trimmed["体积"] = outbound_info_trimmed["货品的长"] * outbound_info_trimmed["货品的宽"] * outbound_info_trimmed["货品的高"]
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
	outbound_info_grouped["物流运单号"] = outbound_info_grouped["物流运单号"].apply(lambda x: sorted(x))
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
	# Sort the "库位编码" for each unique "货品编码" alphabetically
	inventory_grouped["库位编码"] = inventory_grouped["库位编码"].apply(lambda x: sorted(x))
	# Count the number of unique "库位编码" for each unique "货品编码"
	inventory_grouped["库位数量"] = inventory_grouped["库位编码"].apply(len)
	# Use "货品编码" as the key, merge three dataframes
	result = pd.merge(inventory_grouped, weekly_inventory_grouped, how="left", on="货品编码")
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
	# Only keep rows that "出库比例" is not NaN, infinity, and 0
	# result = result[(result["出库比例"].notnull()) & (result["出库比例"] != float("inf")) & (result["出库比例"] != 0)]
	# Sort the result by "动销等级" in descending order
	result = result.sort_values(by="动销等级", ascending=False)
	# Format "出库比例" as percentage
	result["出库比例"] = result["出库比例"].apply(lambda x: f"{x:.2%}")

	# print the result with only "库位编码", "总库存", "出库货品数量", "出库比例" columns
	st.write(result[["库位编码", "库位数量", "总库存", "平均每天库存量", "出库货品数量", "平均每天出库量", "出库比例", "周转天数", "体积", "总库存体积", "总出库体积", "动销等级"]])
