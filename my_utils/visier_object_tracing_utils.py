import os
import zipfile
import pandas as pd
import logging
from datetime import datetime

def unzip_files(zip_folder, extract_to):
    """Unzips all .zip files in the given directory into specified folder."""
    logging.info(f"Starting to unzip files from {zip_folder} to {extract_to}")
    
    zip_count = 0
    for file in os.listdir(zip_folder):
        if file.endswith(".zip"):
            zip_count += 1
            file_path = os.path.join(zip_folder, file)
            folder_name = os.path.splitext(file)[0]
            extract_path = os.path.join(extract_to, folder_name)
            os.makedirs(extract_path, exist_ok=True)

            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                logging.info(f"Extracted: {file} -> {extract_path}")
            except Exception as e:
                logging.error(f"Error extracting {file}: {e}")

    logging.info(f"Completed unzipping {zip_count} files.")

def process_xls_files(base_folder):
    """Reads .xls files from subfolders, extracts required columns, and returns a structured dictionary."""
    logging.info(f"Starting to process .xls files in {base_folder}")
    
    data_dict = {}
    folder_count = 0
    file_count = 0

    for folder in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder)
        if os.path.isdir(folder_path):  
            if "_" not in folder:
                logging.warning(f"Skipping folder. No underscore in folder: {folder})")
                break
            folder_prefix = folder.split("_")[0]
            data_dict[folder_prefix] = {}
            folder_count += 1

            for file in os.listdir(folder_path):
                if file.endswith(".xls"):
                    file_count += 1
                    file_path = os.path.join(folder_path, file)
                    try:
                        xls = pd.ExcelFile(file_path)
                        sheet_names = xls.sheet_names

                        if len(sheet_names) < 2:
                            logging.warning(f"Skipping {file}, insufficient sheets")
                            continue  

                        second_tab = sheet_names[1]  
                        df = xls.parse(second_tab)

                        if "Object Name" in df.columns and "Content Type" in df.columns:
                            data_dict[folder_prefix][second_tab] = df[["Object Name", "Content Type"]].dropna().to_dict(orient="records")
                            logging.info(f"Processed: {file} (Sheet: {second_tab})")
                        else:
                            logging.warning(f"Skipping {file}, missing required columns")

                    except Exception as e:
                        logging.error(f"Error processing {file}: {e}")

    logging.info(f"Completed processing {file_count} .xls files across {folder_count} folders.")
    return data_dict

def save_to_excel(data_dict, output_folder, timestamp):
    """Saves the structured dictionary into an Excel file with a timestamped filename."""
    output_file = os.path.join(output_folder, f"visier_objects_{timestamp}.xlsx")

    rows = []
    for folder_prefix, sheets in data_dict.items():
        for tab_name, records in sheets.items():
            for record in records:
                rows.append([folder_prefix, tab_name, record["Object Name"], record["Content Type"]])

    df = pd.DataFrame(rows, columns=["Tenant Name", "Analytic Object", "Object Name", "Content Type"])
    try:
        df.to_excel(output_file, index=False, engine="openpyxl")
        logging.info(f"Processed data saved to {output_file}")
    except Exception as e:
        logging.error(f"Error saving file {output_file}: {e}")

    return output_file

def safe_click(page, role, name):
    """Safely waits for an element and clicks it, with exception handling."""
    try:
        logging.info(f"Waiting for {name} button to be visible")
        page.get_by_role(role, name=name).wait_for(state="visible", timeout=30000)
        logging.info(f"Clicking {name} button")
        page.get_by_role(role, name=name).click()
    except TimeoutError:
        logging.error(f"Timeout: {name} button not found or not clickable")
    except Exception as e:
        logging.error(f"Error clicking {name} button: {e}")