import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

QUESTION_AMOUNT= 5
MAX_WORKERS = 10
PROMPT_VERSION = ["v0" , "v1", "v2"]


def get_subdirs(directory):
    return [entry.path for entry in os.scandir(directory) if entry.is_dir()]


def run_experiment(subdir: str, prompt_version: str ) -> None:
    print(f"+++++++ {subdir} ({prompt_version}) +++++++")
    config_path = os.path.join(subdir, f"config_0.json")
    output_json = os.path.join(subdir, f"output_mistral_{prompt_version}.json")
    output_log = os.path.join(subdir, f"out_mistral_{prompt_version}.log")
    output_out = os.path.join(subdir, f"out_mistral_{prompt_version}.json")
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
        "--prompt-version",
        prompt_version,
    ]
    subprocess.run(command)

def all_questions():
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for q_index in range(QUESTION_AMOUNT):
            directory = f"config/question_{q_index}"
            print(f"+++++++ QUESTION {q_index} +++++++")
            subdirs = get_subdirs(directory)
            for subdir in subdirs:
                for version in PROMPT_VERSION:
                    executor.submit(run_experiment, subdir, version)


if __name__ == "__main__":
    all_questions()
