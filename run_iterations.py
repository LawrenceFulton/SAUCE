import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

QUESTION_NUMBER = "4"
DIR = f"config/configs_{QUESTION_NUMBER}"
VERSIONS = ["v0", "v1", "v2"]
MAX_WORKERS = 10


def get_subdirs(directory):
    return [entry.path for entry in os.scandir(directory) if entry.is_dir()]


def run_experiment(subdir, version):
    print(f"+++++++ {subdir} ({version}) +++++++")
    config_path = os.path.join(subdir, "config_0.json")
    output_json = os.path.join(subdir, f"output_{version}.json")
    output_log = os.path.join(subdir, f"out_{version}.log")
    output_out = os.path.join(subdir, f"out_{version}.json")
    command = [
        "python",
        "main.py",
        config_path,
        "--json",
        "--output-json",
        output_json,
        "--output-log",
        output_log,
        "-o",
        output_out,
        "--pretty-print",
    ]
    subprocess.run(command)


def main():
    print(f"+++++++ QUESTION {QUESTION_NUMBER} +++++++")
    subdirs = get_subdirs(DIR)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for subdir in subdirs:
            for version in VERSIONS:
                executor.submit(run_experiment, subdir, version)


if __name__ == "__main__":
    main()
