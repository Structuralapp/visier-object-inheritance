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
    files_to_process = ['Subjects.xls'
                        'Selection_Groups.xls',
                        'Selection_Concepts.xls',
                        'Range_Dimensions.xls',
                        'Overlays.xls',
                        'Multi_Subject_Rules.xls',
                        'Modules.xls',
                        'Metrics.xls',
                        'Member_Maps.xls',
                        'Mappings.xls',
                        'Internal_Comparisons.xls',
                        'Events.xls',
                        'Dimensions.xls',
                        'Currencies.xls',
                        'Business_Rules.xls',
                        'Business_Calendar.xls',
                        'Analyses.xls']

    for folder in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder)
        if os.path.isdir(folder_path):  
            if "_" not in folder:
                logging.warning(f"Skipping folder. No underscore in folder: {folder})")
                break
            folder_prefix = folder.split("_")[0]
            data_dict[folder_prefix] = {}
            folder_count += 1

            for file in files_to_process:
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

                        # Define required and optional columns
                        required_columns = ["Object Name", "Content Type"]
                        optional_columns = ["Related Applications", "Tags", "Display Name"]

                        # Mapping for Content Type values
                        content_type_mapping = {
                            "Custom": "Tenant",
                            "Modified Default": "Tenant override",
                            "Default": "Blueprint"
}

                        # Check if required columns exist
                        if all(col in df.columns for col in required_columns):
                            # Ensure optional columns exist, adding them with None if missing
                            for col in optional_columns:
                                if col not in df.columns:
                                    df[col] = None
                            
                            # Apply mapping to "Content Type" column
                            df["Content Type"] = df["Content Type"].map(content_type_mapping).fillna(df["Content Type"])
                            # Select only relevant columns
                            selected_columns = required_columns + optional_columns
                            data_dict[folder_prefix][second_tab] = df[selected_columns].dropna(subset=required_columns).to_dict(orient="records")

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
                rows.append([folder_prefix, tab_name, record["Display Name"], record["Object Name"], record["Tags"], record["Related Applications"], record["Content Type"]])

    df = pd.DataFrame(rows, columns=["Tenant Name", "Analytic Object", "Display Name", "Object Name", "Tags", "Related Applications", "Content Type"])
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