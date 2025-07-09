import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

QUESTION_AMOUNT = 1
MAX_WORKERS = 10
PROMPT_VERSION = ["v0", "v1", "v2"]
REPETITIONS = 6
LLM_NAME = "41-mini"  # Change this to the desired LLM name


def get_subdirs(directory):
    return [entry.path for entry in os.scandir(directory) if entry.is_dir()]


def run_experiment(subdir: str, prompt_version: str, repetition: int) -> None:
    print(f"+++++++Repetition {repetition}: {subdir} ({prompt_version}) +++++++")
    config_path = os.path.join(subdir, f"config_0.json")
    output_out = os.path.join(
        subdir, f"out_{LLM_NAME}_{prompt_version}_{repetition}.json"
    )
    command = [
        "python",
        "main.py",
        config_path,
        "--json",
        "-o",
        output_out,
        "--pretty-print",
        "--prompt-version",
        prompt_version,
    ]
    subprocess.run(command)


def all_questions():
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for repetition in range(REPETITIONS):
            for q_index in range(QUESTION_AMOUNT):
                directory = f"config/question_{q_index}"
                print(f"+++++++ QUESTION {q_index} +++++++")
                subdirs = get_subdirs(directory)
                for subdir in subdirs:
                    for version in PROMPT_VERSION:
                        executor.submit(run_experiment, subdir, version, repetition)


if __name__ == "__main__":
    all_questions()
