# Healthy Brain Study - Data Request Tool

## Getting Started

To get started with the Data Request Tool, clone this repository to your local machine and follow the instructions below.

## Installation

### Step 1: Install PEP
Install PEP, depending on your operating system:
- **Mac/Linux:**
  - Install Docker Desktop
    - Link: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
  - Start Docker Desktop
- **HPC:**
  - Download client.sif and place it in the main folder of the repository.
    - Link: [https://pep.cs.ru.nl/hb/prod/client.sif](https://pep.cs.ru.nl/hb/prod/client.sif)
- **Windows:**
  - Install PEP via the link below, click on ‘for the Healthy Brain environment’
    - Link: [https://gitlab.pep.cs.ru.nl/pep-public/user-docs/-/wikis/home#acquiring-the-software](https://gitlab.pep.cs.ru.nl/pep-public/user-docs/-/wikis/home#acquiring-the-software)

### Step 2: Unzip the downloaded tool
Unzip the tool .zip file and open the folder in terminal.

#### For Windows users
1. Unzip the file in explorer
2. Open the command prompt:
   - Press Win + R to open the Run dialog.
   - Type `cmd` and press Enter or click OK.
3. Navigate to the folder:
   - Use the `cd` (change directory) command to navigate to your desired folder. For example, if you want to go to the unzipped folder which is located in `C:\Path\To\data-request-tool`, you would type:
     - `cd C:\Path\To\data-request-tool`
     - Press Enter.

#### For Mac/Linux users
1. Unzip the file in explorer
2. Open the terminal:
   - On macOS, you can find the Terminal in /Applications/Utilities/ or search for it using Spotlight (Cmd + Space and type "Terminal").
   - In Linux, the Terminal can typically be found in the applications menu, though this varies by distribution. Usually ctrl + alt + t is a shortcut in Linux distributions to open the terminal.
3. Navigate to the folder:
   - Use the `cd` command as in Windows, but with Unix-style paths. For example, to navigate to a folder named `/path/to/data-request-tool` in your user directory:
     - `cd /path/to/data-request-tool`

### Step 3: Run the starter script
Run the starter script, either `start.bat` for Windows or `start.sh` if you are using Mac/Linux. Here follow the instructions on running these scripts:

#### Requirements
- **Windows:**
  - Ensure that Anaconda is installed and accessible via the system PATH or installed at `C:\ProgramData\Anaconda3` or at `C:\Users\%USERNAME%\Anaconda3`. Otherwise, ensure that Python 3 is available either by running `python` or `python3` in PowerShell.
- **Mac/Linux:**
  - Ensure that Anaconda is installed, or the anaconda3 module is available. Otherwise, ensure that Python 3 is installed.

#### Running the script

##### For Windows users
`start.bat`: This script checks for Python and required dependencies, sets up the environment, and runs the application. It ensures all necessary packages are installed and manages Conda environments automatically.
1. Navigate to the folder in explorer
2. Double click on `start.bat`
3. Click on ‘run’

##### For Mac/Linux users
`start.sh`: Similar to the .bat script, this Bash script prepares the environment, checks for dependencies, and runs the Python application. It handles module loading and environment activation.
1. Open a terminal window.
2. Navigate to the directory containing `start.sh`.
3. Make the script executable if it's not already by opening the file explorer, right click the file `start.sh` and selecting ‘Allow to run this file as program’.
4. Execute the script by typing `./start.sh` in terminal and pressing Enter.

### Step 4: Complete download
Follow the steps in the application to complete the download
After the download is finished please follow the steps in the application to unzip the downloaded files.
If this went successfully you can optionally combine the column files into 1 csv per column
