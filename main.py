import pandas as pd
import os
import re
import streamlit as st

# Set the page configuration
st.set_page_config(page_title="出库比例报表",
				   page_icon=":bar_chart:",
				   layout="centered")
# Define the title of the web app
st.title("出库比例报表")
# Define source_files folder
source_files_folder = 'source_files'
# List all files in the directory
all_files = os.listdir(source_files_folder)

# Define the regular expression pattern
ob_info_file_pattern = re.compile(r'^出库单报表.*\.xlsx$')
inventory_file_pattern = re.compile(r'^库存明细.*\.xlsx$')
# Filter files that match the pattern
ob_info_matching_files = [f for f in all_files if ob_info_file_pattern.match(f)]
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
outbound_info_trimmed = outbound_info[["货品编码", "出库货品数量"]]
# For inventory, trim the columns, only keep columns with indices of names "库位编码", "货品编码" and "总库存"
inventory_trimmed = inventory[["库位编码", "货品编码", "总库存"]]

# For outbound info, use "货品编码" as the key, sum up the "出库货品数量" for each unique "货品编码"
outbound_info_grouped = outbound_info_trimmed.groupby("货品编码").sum()
# For inventory, use "货品编码" as the key, sum up the "总库存" for each unique "货品编码"
inventory_grouped = inventory_trimmed.groupby("货品编码").sum()
# Use "货品编码" as the key, find all "库位编码" for each unique "货品编码"
inventory_grouped["库位编码"] = inventory_trimmed.groupby("货品编码")["库位编码"].apply(list)
# Remove duplicate "库位编码" for each unique "货品编码"
inventory_grouped["库位编码"] = inventory_grouped["库位编码"].apply(lambda x: list(set(x)))
# Sort the "库位编码" for each unique "货品编码" alphabetically
inventory_grouped["库位编码"] = inventory_grouped["库位编码"].apply(lambda x: sorted(x))
# Use "货品编码" as the key, merge the two dataframes
result = pd.merge(inventory_grouped, outbound_info_grouped, on="货品编码", how="left")
# Calculate outbound ratio
result["出库比例"] = result["出库货品数量"] / result["总库存"]
# Only keep rows that "出库比例" is not NaN, infinity, and 0
result = result[(result["出库比例"].notnull()) & (result["出库比例"] != float("inf")) & (result["出库比例"] != 0)]
# Sort the result by "出库比例" in ascending order
result.sort_values("出库比例", inplace=True)
# Format "出库比例" as percentage
result["出库比例"] = result["出库比例"].apply(lambda x: f"{x:.2%}")
# Put outbound ratio to the last column
result = result[[c for c in result if c not in ["出库比例"]] + ["出库比例"]]

# print the result
st.write(result)
