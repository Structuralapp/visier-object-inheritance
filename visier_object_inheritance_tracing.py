import os
import time
from playwright.sync_api import Playwright, sync_playwright
import pandas as pd
import shutil
import logging
from datetime import datetime
import sys
import yaml
from my_utils.visier_object_tracing_utils import *


# Get the directory where the .exe file is located
base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd()

# Define folders relative to the .exe location
zip_folder = os.path.join(base_path, "zip")
extract_folder = os.path.join(base_path, "extract")
output_folder = os.path.join(base_path, "output")
logs_folder = os.path.join(base_path, "logs")
download_path = os.path.join(os.getcwd(), "zip")

# Timestamp for filenames
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Ensure logs folder exists
os.makedirs(logs_folder, exist_ok=True)

# Setup logging
log_file = os.path.join(logs_folder, f"process_log_{timestamp}.log")
logging.basicConfig(
    # filename=log_file, 
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_file),  # Log to a file
        logging.StreamHandler(sys.stdout)  # Log to terminal
    ]
)

try:
    # Read config file
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    env = config['general']['default_env']
    # Reading username and password
    try:
        username = config[env]['credentials']['username']
    except KeyError:
        raise ValueError("Missing 'username' in the config file under 'credentials' section.")
    
    try:
        password = config[env]['credentials']['password']
    except KeyError:
        raise ValueError("Missing 'password' in the config file under 'credentials' section.")

    # Reading tenants
    try:
        tenants = [x.strip() for x in config[env]['settings']['tenants'].split(',')]
    except KeyError:
        raise ValueError("Missing 'tenants' in the config file under 'settings' section.")
    except AttributeError:
        raise ValueError("'tenants' in the config file should be a comma-separated string.")
    
    # Reading vanity_name
    try:
        vanity_name = config[env]['settings']['vanity_name']
    except KeyError:
        raise ValueError("Missing 'vanity_name' in the config file under 'settings' section.")
    
        # Reading browser type
    try:
        browser_type = config[env]['settings']['browser_type'].lower()
    except KeyError:
        raise ValueError("Missing 'browser_type' in the config file under 'settings' section.")
    
    # Reading headless (boolean value)
    try:
        headless = bool(config[env]['settings']['headless'])
    except KeyError:
        raise ValueError("Missing 'headless' in the config file under 'settings' section.")
    except ValueError:
        raise ValueError("Invalid value for 'headless'. It should be a boolean (True/False).")

except FileNotFoundError:
    logging.exception("Error: Configuration file 'config.yaml' not found.")
    sys.exit(1)
except Exception as e:
    logging.exception(f"Error: {e}")
    sys.exit(1)

logging.info("Configuration loaded successfully.")

def download_for_tenant(page, tenant):
    """Handles the entire download process for a given tenant."""
    logging.info(f"Starting processing for tenant: {tenant}")
    try:
        page1 = page
        if tenant != 'Augeo':
            # Wait for the correct tenant row to appear
            page.wait_for_selector(f"div[row-id='{tenant}'] clr-icon[data-idx='3']", timeout=60000)

            with page.expect_popup() as page1_info:
                logging.info(f"Clicking on tenant row: {tenant}")
                page.locator(f"div[row-id='{tenant}'] clr-icon[data-idx='3']").click(force=True)

            page1 = page1_info.value
            logging.info(f"Popup window opened for tenant: {tenant}")

        # Click through navigation steps
        safe_click(page1, "gridcell", "Release")
        safe_click(page1, "button", "Model")
        safe_click(page1, "button", "Settings")
        safe_click(page1, "button", "Application Definition")
        safe_click(page1, "button", "Download Application")

        logging.info(f"Waiting for download to start for tenant: {tenant}")
        with page1.expect_download(timeout=300000) as download_info:
            download = download_info.value

        # Rename file with tenant name
        new_filename = f"{tenant}_{download.suggested_filename}" if tenant == "Augeo" else f"{tenant.split('~')[1].capitalize()}_{download.suggested_filename}" 
        download_path_final = os.path.join(download_path, new_filename)

        # Wait for download to complete
        while not download.path():
            logging.info(f"Waiting for file download to complete: {tenant}")
            time.sleep(5)

        download.save_as(download_path_final)
        logging.info(f"Download completed for {tenant}: {download_path_final}")
    except TimeoutError:
        logging.error(f"Timeout: Tenant {tenant} row did not appear in time.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error processing tenant {tenant}: {e}")
        sys.exit(1)

def run(playwright: Playwright) -> None:
    logging.info(f"Opening a {browser_type} browser in headless mode set to '{headless}'.")
    browser = playwright.chromium.launch(channel=browser_type if browser_type == "chrome" else None, headless=headless)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()
    try:
        # Login once
        logging.info("Navigating to login page")
        page.goto(f"https://{vanity_name}.visier.com/VServer/auth")
        
        if vanity_name == 'augeointegration':
            page.get_by_role("textbox", name="Username").fill(username)
            page.get_by_role("textbox", name="Password").fill(password)
            page.get_by_role("button", name="Sign in").click()
            # Wait for main page to load
            page.wait_for_selector("div[row-id]", timeout=60000)
            tenantPage = page
        else:
            page.get_by_role("textbox", name="Username").click()
            page.get_by_role("textbox", name="Username").fill(username)
            page.get_by_role("textbox", name="Username").press("Tab")
            page.get_by_role("textbox", name="Password").fill(password)
            page.get_by_role("button", name="Sign In").click()
            page.get_by_role("button", name="Send Push").click()
            logging.info("Waiting for user to approve push notification...")
            page.wait_for_selector("span.tool-title:text('Home')", timeout=60000)
            logging.info("Push approved, proceeding to the next step.")
            with page.expect_popup() as page1_info:
                page.get_by_role("listitem").filter(has_text="Studio").locator("span").first.click()
            page1 = page1_info.value
            parentPage = page1.url

            page1.get_by_role("link", name="Projects").click()
            
            download_for_tenant(page1, 'Augeo')

            page1.goto(parentPage)
            page1.get_by_role("link", name="Tenants").click()
            tenantPage = page1

    except TimeoutError:
        logging.error("Timeout: Login page elements did not load in time.")
        return
    except Exception as e:
        logging.error(f"Error during login: {e}")
        return

    # Iterate over tenants and download for each one
    for tenant in tenants:
        try:
            download_for_tenant(tenantPage, tenant)
            time.sleep(5)  # Small delay before opening next tenant popup
        except Exception as e:
            logging.error(f"Unexpected error for tenant {tenant}: {e}")

    logging.info("Closing browser session")

    context.close()
    browser.close()

def main():
    """Main function to orchestrate the entire workflow."""
    logging.info("Starting script execution")

    try:
        # Remove and recreate necessary folders
        if os.path.exists(extract_folder):
            shutil.rmtree(extract_folder)
            logging.info(f"Deleted existing extract folder: {extract_folder}")

        if os.path.exists(zip_folder):
            shutil.rmtree(zip_folder)
            logging.info(f"Deleted existing extract folder: {zip_folder}")

        os.makedirs(extract_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(zip_folder, exist_ok=True)
    except Exception as e:
        logging.error(f"Error during file cleanup: {e}", exc_info=True)

    try:
        logging.info("Starting Playwright session")
        with sync_playwright() as playwright:
            run(playwright)  # Run Playwright automation

        unzip_files(zip_folder, extract_folder)

        data_dict = process_xls_files(extract_folder)

        save_to_excel(data_dict, output_folder, timestamp)

        logging.info("Script execution completed successfully")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()