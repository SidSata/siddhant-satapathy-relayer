import subprocess

# Define the command and parameters
command = "python"
script_name = "get-largest-block.py"
db_path = "db.sqlite3"
start_date = "2024-01-01 00:00:00"
end_date = "2024-01-01 00:30:00"

# Execute the script with the given parameters
subprocess.run([command, script_name, db_path, start_date, end_date])