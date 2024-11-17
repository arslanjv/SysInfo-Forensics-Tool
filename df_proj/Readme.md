# SysInfo Forensics Tool

_SYSInfo Forensics Tool_ is a Python-based project designed to assist in digital forensic investigations by gathering detailed system information from both live systems and Exported Registry files. The tool leverages Python and Flask to provide an accessible web-based interface for investigators and analysts.

## Features

- **Live System Scan**: Gather detailed system information from the current running system.
- **Forensics Scan**: Analyze Exported Registry files (like SYSTEM, SAM, SOFTWARE, SECUIRTY etc.) to extract system information from it.
- **JSON Output**: Outputs collected data in a structured JSON format for further analysis.
- **Modular Design**: Separate scripts for forensic analysis and system information gathering.
- **Web Application Interface**: Flask-based web app for user-friendly interaction.

## Requirements

- Python 3.12.5 or later
- Flask

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/arslanjv/SysInfo-Forensics-Tool.git
   cd SysInfo-Forensics-Tool/df_proj
   ```

2. **Set up a virtual environment** (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  #for Linux/MacOS
   venv\Scripts\activate     #for Windows
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:

   ```bash
   python app.py
   ```

5. **Access the web app**:
   Open a web browser and navigate to http://127.0.0.1:5000.

## Usage

### 1. Live System Scan

- Launch the application and select the "Live System Scan" option.
- The tool will collect system information of the host machine and present the results in a structured format.

### 2. Forensics Scan

- Enter folder path containing extracted Registry files in the Forensics Analysis Webpage.
- The tool will analyze the files and extract system information from it.

### 3. Output

- The results of the scans are saved in JSON format, such as SysInfo.json or forensics1.json, for further investigation.

## Contribution

Contributions are welcome! If you'd like to improve the tool or add features, feel free to submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

This project is developed as part of a digital forensics semester project by a group of four students in their 5th semester.

- [Muhammad Arsalan Javed](https://github.com/arslanjv)
- [Hafiz Mustafa Zain](https://github.com/mustafaazain)
- [Ahmed Shahzad Zia](https://github.com/ChapriCheater)
- [Ahmed Tahir]()
