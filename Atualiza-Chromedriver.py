import requests
import wget
import zipfile
import os
import shutil
from subprocess import run, PIPE

def atualiza(self):
    bin_folder_path = "bin"
    os.makedirs(bin_folder_path, exist_ok=True)

    def get_actual_chromedriver_path(folder):
        """Find the ChromeDriver binary in the specified folder."""
        pattern = os.path.join(folder, "chromedriver.exe")  # Explicitly look for .exe file
        if os.path.exists(pattern):
            return pattern
        return None

    def get_latest_chromedriver_version():
        """Fetch the latest stable ChromeDriver version."""
        url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data['channels']['Stable']['version']
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch ChromeDriver version: {e}")
        except:
            raise RuntimeError("Failed to parse JSON data or find the expected structure.")
    
    def get_local_chromedriver_version(driver_path):
        """Get the version of the local ChromeDriver."""
        if driver_path and os.path.exists(driver_path):
            result = run([driver_path, "--version"], stdout=PIPE, stderr=PIPE, text=True)
            if result.returncode == 0:
                return result.stdout.split(" ")[1].strip()
        return None
    
    chrome_driver_path = get_actual_chromedriver_path(bin_folder_path)
    local_version = get_local_chromedriver_version(chrome_driver_path)
    latest_version = get_latest_chromedriver_version()
    
    if not local_version or local_version.split(".")[0] != latest_version.split(".")[0]:
        print('Atualizando o chromedriver')
        
        download_url = f"https://storage.googleapis.com/chrome-for-testing-public/{latest_version}/win64/chromedriver-win64.zip"

        # Download the zip file using the URL built above
        latest_driver_zip = wget.download(download_url, 'chromedriver.zip')

        # Ensure the bin directory exists
        destination_folder = os.path.join('bin')
        os.makedirs(destination_folder, exist_ok=True)

        # Move the downloaded ZIP file into the bin directory
        destination_zip = os.path.join(destination_folder, os.path.basename(latest_driver_zip))
        shutil.move(latest_driver_zip, destination_zip)

        # Extract the ZIP file into the bin directory
        with zipfile.ZipFile(destination_zip, 'r') as zip_ref:
            zip_ref.extractall(destination_folder)

        # Path of the extracted folder
        extracted_folder = os.path.join(destination_folder, 'chromedriver-win64')

        # Move "chromedriver.exe" to the "bin" folder
        chromedriver_path = os.path.join(extracted_folder, 'chromedriver.exe')

        if os.path.exists(chromedriver_path):
            if chrome_driver_path:  # Only remove if it exists
                os.remove(chrome_driver_path)  # Remove the existing file
            shutil.move(chromedriver_path, destination_folder)

        # Delete the extracted folder
        shutil.rmtree(extracted_folder)

        # Delete the ZIP file after extraction
        os.remove(destination_zip)
        print(f'\nChromedriver atualizado com sucesso para a versão {latest_version}.\n')
