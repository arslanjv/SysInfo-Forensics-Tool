# app.py
from flask import Flask, render_template, redirect, url_for, request, flash
import json
import os
import subprocess  # Import subprocess to run external scripts
from sysinfo_script import gather_system_info

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For flash messages

@app.route("/")
def main():
    return render_template("main.html")

@app.route("/live-system-analysis")
def live_system_analysis():
    gather_system_info()
    with open("SysInfo.json", "r") as json_file:
        system_info = json.load(json_file)
    return render_template("system_info.html", system_info=system_info)

@app.route("/forensic-image-analysis", methods=["GET", "POST"])
def forensic_image_analysis():
    if request.method == "POST":
        image_path = request.form.get("image_path")
        
        if not image_path or not os.path.exists(image_path):
            flash("Invalid file path")
            return redirect(url_for('forensic_image_analysis'))

        try:
            # Run the forensics analysis script on the specified path using subprocess
            result = subprocess.run(
                ['python', 'forensics_script.py', image_path],
                capture_output=True, text=True
            )
            print(f"Subprocess result: {result.stdout}")  # Debug print

            # Check if forensics1.json was generated
            if os.path.exists('forensics1.json'):
                print("Forensics1.json found!")  # Debug print
                with open("forensics1.json", "r") as json_file:
                    forensic_data = json.load(json_file)
                    print(f"Forensic data: {forensic_data}")  # Debug print

                # Render forensics_info.html with the forensic data passed as system_info
                return render_template("forensics_info.html", system_info=forensic_data)
            else:
                flash("Error: Forensic data not generated.")
                return redirect(url_for('forensic_image_analysis'))

        except Exception as e:
            flash(f"An error occurred during analysis: {e}")
            return redirect(url_for('forensic_image_analysis'))

    return render_template("forensics.html")
if __name__ == "__main__":
    app.run(debug=False)
