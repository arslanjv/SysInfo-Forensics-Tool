import sys
import os
import json
from Registry import Registry
from datetime import datetime, timezone

# Function to convert FILETIME to a timezone-aware UTC datetime
def filetime_to_datetime(filetime):
    return datetime.fromtimestamp((filetime - 116444736000000000) / 10000000, timezone.utc)

# Function to find registry hive files
def find_hive_files(folder_path, hive_name):
    for root, dirs, files in os.walk(folder_path):
        if hive_name in files:
            return os.path.join(root, hive_name)
    return None

# Get the folder path from the command line argument
folder_path = sys.argv[1]  # This will get the image path passed from the app.py

# Locate the SOFTWARE, SAM, SYSTEM, and SECURITY files
software_hive_path = find_hive_files(folder_path, "software")
sam_hive_path = find_hive_files(folder_path, "SAM")
system_hive_path = find_hive_files(folder_path, "system")
security_hive_path = find_hive_files(folder_path, "SECURITY")

# Initialize a dictionary to store all the forensic data
forensic_data = {}

# Extract OS information from the SOFTWARE hive
if software_hive_path:
    try:
        software_hive = Registry.Registry(software_hive_path)
        os_key_path = "Microsoft\\Windows NT\\CurrentVersion"
        os_key = software_hive.open(os_key_path)

        forensic_data["OS"] = {
            "Name": os_key.value("ProductName").value(),
            "Release ID": os_key.value("ReleaseId").value(),
            "Current Build": os_key.value("CurrentBuild").value(),
            "Version": os_key.value("DisplayVersion").value(),
        }
    except Exception as e:
        print(f"An error occurred while processing SOFTWARE hive: {e}")
else:
    print("SOFTWARE hive not found in the specified folder.")

# Extract user count and list user names from the SAM hive
if sam_hive_path:
    try:
        sam_hive = Registry.Registry(sam_hive_path)
        user_key_path = "SAM\\Domains\\Account\\Users\\Names"
        user_key = sam_hive.open(user_key_path)
        
        # Extract user accounts and build the dictionary
        users = [subkey.name() for subkey in user_key.subkeys()]
        user_data = {"total users": len(users)}
        
        # Add user names to the forensic data, using a numbered pattern
        for i, user in enumerate(users, start=1):
            user_data[f"user {i:02}"] = user
        
        forensic_data["Users"] = user_data
        
    except Exception as e:
        forensic_data["Users"] = {"Error": "User Accounts not found"}
else:
    print("SAM hive not found in the specified folder.")

# Extract computer name, processor details, HDD/SSD details, shutdown time, and system model/manufacturer from the SYSTEM hive
if system_hive_path:
    try:
        system_hive = Registry.Registry(system_hive_path)

        # Computer name
        computer_name_key_path = "ControlSet001\\Control\\ComputerName\\ComputerName"
        computer_name_key = system_hive.open(computer_name_key_path)
        forensic_data["Computer"] = {
            "Name": computer_name_key.value("ComputerName").value()
        }

        # Processor details
        processor_key_path = "ControlSet001\\Enum\\ACPI"
        processor_key = system_hive.open(processor_key_path)
        for subkey in processor_key.subkeys():
            if "GenuineIntel" in subkey.name() or "AuthenticAMD" in subkey.name():
                processor_name = subkey.name().split('-')[-2]
                trimmed_name = subkey.name().split('-')[-1]  
                forensic_data["Processor"] = {
                    "Identifier": subkey.name().split('-')[1],
                    "ProcessorName": processor_name,
                    "ProcessorType": trimmed_name
                }
                break

        # HDD/SSD details
        scsi_key_path = "ControlSet001\\Enum\\SCSI"
        hdd_details = {}
        try:
            scsi_key = system_hive.open(scsi_key_path)
            for index, subkey in enumerate(scsi_key.subkeys()):
                for device_key in subkey.subkeys():
                    try:
                        device_name = device_key.value("FriendlyName").value()
                        hdd_details[str(index)] = device_name.split(';')[-1]
                    except Exception:
                        pass
            forensic_data["Storage"] = hdd_details
        except Exception:
            forensic_data["Storage"] = "Details not found"

        # Shutdown time
        shutdown_time_key_path = "ControlSet001\\Control\\Windows"
        shutdown_time_key = system_hive.open(shutdown_time_key_path)
        shutdown_time = shutdown_time_key.value("ShutdownTime").value()
        readable_shutdown_time = filetime_to_datetime(int.from_bytes(shutdown_time, "little"))
        forensic_data["Shutdown"] = {"Last Shutdown Time": str(readable_shutdown_time)}

        # Motherboard details
        try:
            motherboard_key_path_1 = "ControlSet001\\Enum\\Root\\ACPI_HAL\\0000"
            motherboard_key = system_hive.open(motherboard_key_path_1)
            motherboard_name = motherboard_key.value("DeviceDesc").value().split(';')[-1]
            forensic_data["Motherboard"] = {"Details": motherboard_name}
        except Exception:
            try:
                motherboard_key_path_2 = "ControlSet001\\Enum\\ACPI_HAL"
                motherboard_key = system_hive.open(motherboard_key_path_2)
                motherboard_name = motherboard_key.value("DeviceDesc").value().split(';')[-1]
                forensic_data["Motherboard"] = {"Details": motherboard_name}
            except Exception:
                forensic_data["Motherboard"] = {"Details": "Motherboard details not found"}

        # System model and manufacturer
        try:
            hardware_config_key = system_hive.open("HardwareConfig")
            first_uuid_key = hardware_config_key.subkeys()[0]
            system_model_key_path = f"HardwareConfig\\{first_uuid_key.name()}"
            system_model_key = system_hive.open(system_model_key_path)

            system_model = system_model_key.value("SystemProductName").value() 
            manufacturer = system_model_key.value("SystemManufacturer").value()
            SystemSKU = system_model_key.value("SystemSKU").value()
            SystemVersion = system_model_key.value("SystemVersion").value()
            BIOSVendor = system_model_key.value("BIOSVendor").value()
            BIOSVersion = system_model_key.value("BIOSVersion").value()
            BIOSReleaseDate = system_model_key.value("BIOSReleaseDate").value()
            forensic_data["System"] = {
                "Model": system_model,
                "Manufacturer": manufacturer,
                "SystemSKU":SystemSKU,
                "SystemVersion":SystemVersion
            }
            forensic_data["BIOS Info"] = {
                "BIOSVendor": BIOSVendor,
                "BIOSVersion": BIOSVersion,
                "BIOSReleaseDate": BIOSReleaseDate
            }
        except Registry.RegistryKeyNotFoundException:
            forensic_data["System"] = {"Model": "Key not found", "Manufacturer": "Key not found", "SystemSKU": "Key not found", "SystemVersion": "Key not found"}
            forensic_data["BIOS Info"] = {"BIOSVendor": "Key not found", "BIOSVersion": "Key not found", "BIOSReleaseDate": "Key not found"}

    except Exception as e:
        print(f"An error occurred while processing SYSTEM hive: {e}")
else:
    print("SYSTEM hive not found in the specified folder.")

# Extract security policies from the SECURITY hive
if security_hive_path:
    try:
        security_hive = Registry.Registry(security_hive_path)
        
        # Define paths and keys for security policies
        paths_and_keys = {
            "Audit Policies": "Policy\\PolAdtEv",
            "Access Control Policies": "Policy\\PolAcDmS",
            "User Rights Assignment": "Policy\\PolPrDmS"
        }

        # Check for the presence of the security policies
        for description, path in paths_and_keys.items():
            try:
                security_key = security_hive.open(path)
                forensic_data[description] = {"Status": "Present"}
            except Exception:
                forensic_data[description] = {"Status": "Not Found"}
                
    except Exception as e:
        print(f"An error occurred while processing SECURITY hive: {e}")
else:
    print("SECURITY hive not found in the specified folder.")

# Write to a JSON file for frontend access
with open("forensics1.json", "w") as json_file:
    json.dump(forensic_data, json_file, indent=4)
