import subprocess

for i in range(0, 10):
    command = f"python main.py configurations/example_social_welfare.json"
    subprocess.run(command, shell=True)