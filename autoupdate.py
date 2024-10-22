import os
import requests
import zipfile
import io
import shutil
from configparser import ConfigParser

# Hardcoded repository URL
REPO_URL = "https://api.github.com/repos/Wy477-P/UDE"  # Replace with your actual repo URL
def merge_config_files(existing_file, new_file):
    config = ConfigParser()
    config.read(existing_file)

    new_config = ConfigParser()
    new_config.read(new_file)

    for section in new_config.sections():
        if not config.has_section(section):
            config.add_section(section)
        for key, value in new_config.items(section):
            if not config.has_option(section, key):
                config.set(section, key, value)

    with open(existing_file, 'w') as f:
        config.write(f)

def download_and_update(latest_release, directory):
    print("Checking for UDE zip file in the latest release...")
    zip_url = None

    for asset in latest_release['assets']:
        print(f"Found asset: {asset['name']}")
        if "UDE" in asset['name'] and asset['name'].endswith('.zip'):
            zip_url = asset['url']
            break

    if zip_url is None:
        print("No suitable zip file found in the latest release.")
        return

    print(f"Downloading from URL: {zip_url}")

    try:
        # Download the actual asset with proper headers
        headers = {"Accept": "application/octet-stream"}  # Set header to get the raw file
        response = requests.get(zip_url, headers=headers)
        response.raise_for_status()

        # Unzip the downloaded content
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # Extract the content into a temporary directory
            temp_extract_path = os.path.join(directory, "temp_extracted")
            z.extractall(temp_extract_path)

        # Check for folders and files
        extracted_folder = None
        for item in os.listdir(temp_extract_path):
            item_path = os.path.join(temp_extract_path, item)
            if os.path.isdir(item_path):
                extracted_folder = item_path
                break  # Get the first folder

        if extracted_folder is None:
            print("No extracted folders found.")
            return

        # Move files from the extracted folder to the target directory
        for root, dirs, files in os.walk(extracted_folder):
            for file in files:
                s = os.path.join(root, file)
                relative_path = os.path.relpath(s, extracted_folder)
                d = os.path.join(directory, relative_path)

                # Ensure the target directory exists
                os.makedirs(os.path.dirname(d), exist_ok=True)

                if os.path.basename(s) == "autoupdate.py":
                    continue  # Skip replacing the autoupdate script

                if os.path.basename(s) == "Config.ini":
                    merge_config_files(os.path.join(directory, "Config.ini"), s)
                else:
                    shutil.copy2(s, d)  # Copy file, replacing it if it exists

        # Clean up the temporary extraction folder
        shutil.rmtree(temp_extract_path)
    except Exception as e:
        print(f"Error during extraction or file operations: {e}")

def main():
    try:
        directory = os.getcwd()  # Get the current working directory
        response = requests.get(f"{REPO_URL}/releases/latest")
        response.raise_for_status()

        latest_release = response.json()

        print(f"Latest release: {latest_release['tag_name']}")
        
        # Download and update
        download_and_update(latest_release, directory)
    except requests.RequestException as e:
        print(f"Error fetching latest release: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Pause for user input before closing
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
