import subprocess
import json

pipeline = "FullPlate"

# Command to run the script
if pipeline == "FullPlate":
    script_path = "darknet_video_full_detect.py"
    args = ["--gpu_index", "0", "--config_file", "./FullPlates/AntigoPlates_test3.cfg", "--weights", "./FullPlates/AntigoPlates_test3_30000.weights", "--data_file", "./FullPlates/AntigoPlates_test3.data"]
elif pipeline == "OCR":
    script_path = "darknet_video_ocr.py"
    args = ["--gpu_index", "0", "--config_file", "./DiffPlates/DiffPlates.cfg", "--weights", "./DiffPlates/DiffPlates_best.weights", "--data_file", "./DiffPlates/DiffPlates.data"]
else:
    raise ValueError("Pipeline does not exist")

# Run the script
try:
    result = subprocess.run(
        ["python", script_path] + args,
        capture_output=True,  # Capture stdout and stderr
        text=True,           # Decode output to string
        check=True           # Raise exception if script fails
    )
    # Parse the output
    # output = result.stdout.strip()
    # plate_data = json.loads(output)
    # print("Captured Plate:", plate_data["plate"])
    # print("Confidence:", plate_data["confidence"])

except subprocess.CalledProcessError as e:
    print(f"Script failed with error: {e.stderr}")
except json.JSONDecodeError:
    print(f"Failed to parse output")
