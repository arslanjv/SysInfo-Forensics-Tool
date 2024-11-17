import subprocess
import json

def execute_command(command):
    """Executes a PowerShell command and returns the result."""
    try:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip() if result.stdout else "No Data"
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

def convert_to_gb(size_in_bytes):
    """Converts size from bytes to GB."""
    return round(size_in_bytes / (1024 ** 3), 2) if size_in_bytes else 0

def gather_system_info():
    """Gathers system information and returns it in a structured format."""
    system_info = {}
    
    # PowerShell commands to fetch system information
    commands = {
        "Installed OS and Version": "Get-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion' | Select-Object -Property ProductName, CurrentVersion, BuildLabEx | ConvertTo-Json -Depth 1",
        "Boot Time": "(gcim Win32_OperatingSystem).LastBootUpTime | ConvertTo-Json",
        "Current Time": "Get-Date | ConvertTo-Json",
        "BIOS/UEFI Information": "Get-ItemProperty -Path 'HKLM:\\HARDWARE\\DESCRIPTION\\System\\BIOS' | Select-Object -Property BIOSVendor, BIOSVersion, BIOSReleaseDate | ConvertTo-Json",
        "System Model and Manufacturer": "Get-ItemProperty -Path 'HKLM:\\HARDWARE\\DESCRIPTION\\System\\BIOS' | Select-Object -Property SystemManufacturer, SystemProductName | ConvertTo-Json",
        "Installed RAM (GB)": "(Get-CimInstance -ClassName Win32_ComputerSystem).TotalPhysicalMemory / 1GB",
        "Processor Details": "Get-ItemProperty -Path 'HKLM:\\HARDWARE\\DESCRIPTION\\System\\CentralProcessor\\0' | Select-Object -Property ProcessorNameString, Identifier | ConvertTo-Json",
        "HDD/SSD Details": "Get-PhysicalDisk | Select-Object -Property DeviceID, Model, MediaType, Size | ConvertTo-Json -Depth 1",
        "Graphics Card Details": "Get-CimInstance -ClassName Win32_VideoController | Select-Object -Property Name, DriverVersion, VideoProcessor, AdapterRAM | ConvertTo-Json -Depth 1",
        "Motherboard Model": "Get-ItemProperty -Path 'HKLM:\\HARDWARE\\DESCRIPTION\\System\\BIOS' | Select-Object -Property BaseBoardManufacturer, BaseBoardProduct | ConvertTo-Json",
        "System Serial Number": "Get-CimInstance -ClassName Win32_BIOS | Select-Object -Property SerialNumber | ConvertTo-Json",
        "Users": "Get-LocalUser | Select-Object Name | ConvertTo-Json"
    }

    for key, command in commands.items():
        output = execute_command(command)
        try:
            if key == "Installed RAM (GB)":
                system_info[key] = round(float(output), 2)
            elif key == "HDD/SSD Details":
                parsed_output = json.loads(output)
                # Ensure this is a list of dictionaries and extract the details
                system_info[key] = [{
                    "Device ID": h.get("DeviceID"),
                    "Model": h.get("Model"),
                    "Media Type": h.get("MediaType"),
                    "Size (GB)": convert_to_gb(h.get("Size", 0))
                } for h in (parsed_output if isinstance(parsed_output, list) else [parsed_output])]
            elif key == "Graphics Card Details":
                parsed_output = json.loads(output)
                system_info[key] = [{
                    "Name": card["Name"],
                    "Driver Version": card["DriverVersion"],
                    "Video Processor": card["VideoProcessor"],
                    "Adapter RAM (GB)": convert_to_gb(card["AdapterRAM"])
                } for card in (parsed_output if isinstance(parsed_output, list) else [parsed_output])]
            elif key == "Users":
                parsed_output = json.loads(output)
                # Prepare formatted user list with total count
                user_list = {f"user {i+1:02}": user["Name"] for i, user in enumerate(parsed_output)}
                system_info[key] = {
                    "total users": len(parsed_output),
                    **user_list
                }
            else:
                system_info[key] = json.loads(output)
        except (json.JSONDecodeError, SyntaxError):
            system_info[key] = output

    # Remove unnecessary fields
    fields_to_remove = {
        "Boot Time": ["value"],
        "Current Time": ["value", "DisplayHint"]
    }

    def remove_fields(data, fields):
        """Removes specified fields from the data."""
        for field, keys in fields.items():
            if field in data:
                if keys:
                    for key in keys:
                        data[field].pop(key, None)
                else:
                    data.pop(field, None)

    remove_fields(system_info, fields_to_remove)

    # Write the system information to a JSON file
    with open("SysInfo.json", "w") as json_file:
        json.dump(system_info, json_file, indent=4)

    return system_info

if __name__ == "__main__":
    info = gather_system_info()
    print(json.dumps(info, indent=4))
