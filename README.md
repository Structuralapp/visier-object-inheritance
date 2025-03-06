# Project Setup Guide

## 📌 Overview
This project automates downloading, extracting, processing, and saving the Visier application definition data using Playwright and Pandas. Follow the steps below to set up and run the project.

## 📁 Folder Structure
```
project_folder/
│-- zip/         # Store tenant Application definition ZIP files here
│-- extract/     # Extracted unzipped files will be saved here
│-- logs/        # Log files will be stored here
│-- my_utils/    # Utility Python functions
│-- output/      # Final processed files will be saved here
│-- config.yml   # Configuration file for settings
│-- requirements.txt # Dependencies list
│-- visier_object_inheritance_tracing.py    # Main Python script
│-- run.bat      # Batch file to execute the script in windows
```

## 🛠 Prerequisites
Ensure you have the following installed on your system:
- **Python 3.8+** (Check with `python --version`)
- **pip** (Check with `pip --version`)

## 🚀 Setup Steps

### 1️⃣ Install Python (If Not Installed)
Download and install Python from [https://www.python.org/downloads/](https://www.python.org/downloads/). Ensure to check the option **"Add Python to PATH"** during installation.

### 2️⃣ Create a Virtual Environment
Open a terminal or command prompt and navigate to the project folder:
```sh
cd path\to\project_folder
```
Create a virtual environment named `visier-object-trace`:
```sh
python -m venv visier-object-trace
```
Activate the virtual environment:
- **Windows:**  
  ```sh
  visier-object-trace\Scripts\activate
  ```
- **Mac/Linux:**  
  ```sh
  source visier-object-trace/bin/activate
  ```

### 3️⃣ Install Required Packages
Once the virtual environment is activated, install dependencies:
```sh
pip install -r requirements.txt
```

### 4️⃣ Configure Settings
Edit `config.yml` and update your credentials and settings (for augeointegration and augeo environments):
```yaml
general:
  default_env: augeointegration
augeointegration:
  credentials:
    username: your_username
    password: your_password
  settings:
    tenants: tenant1,tenant2
    vanity_name: augeointegration
    headless: true
    browser_type: chrome
```

### 5️⃣ Run the Project
Execute the batch file to run the Python script:
```sh
run.bat
```
This will:
1. Create the virtual environment if not present.
2. Activate the virtual environment
3. Run the `visier_object_inheritance_tracing.py`
4. Log messages will be displayed in the terminal and saved in `logs/`

### 6️⃣ Deactivating the Virtual Environment
After running the script, you can deactivate the virtual environment:
```sh
deactivate
```

## 📝 Notes
- If you encounter issues with dependencies, try running `pip install --upgrade pip` before installing requirements.
- Logs are saved in the `logs/` folder. Check them for debugging issues.

