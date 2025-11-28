import os
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor

QUESTIONS = [0,1,2,3,4]
MAX_WORKERS = 20
PROMPT_VERSION = ["v0", "v1", "v2"]
REPETITIONS = 5


def get_subdirs(directory):
    return [entry.path for entry in os.scandir(directory) if entry.is_dir()]


def run_experiment(subdir: str, prompt_version: str, repetition: int, llm_name: str) -> None:
    print(f"+++++++Repetition {repetition}: {subdir} ({prompt_version}) +++++++")
    config_path = os.path.join(subdir, f"config_{repetition}.json")
    output_out = os.path.join(
        subdir, f"out_{llm_name}_{prompt_version}_{repetition}.json"
    )

    if not os.path.exists(output_out) or os.path.getsize(output_out) == 0:

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
    else:
        print(f"Skipping {output_out}, already exists and is not empty.")



def all_questions(llm_name: str):
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for repetition in range(REPETITIONS):
            for q_index in QUESTIONS:
                directory = f"config/question_{q_index}"
                print(f"+++++++ QUESTION {q_index} +++++++")
                subdirs = get_subdirs(directory)
                for subdir in subdirs:
                    for version in PROMPT_VERSION:
                        executor.submit(run_experiment, subdir, version, repetition, llm_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm-name", type=str, required=True, help="Name of the LLM used")
    args = parser.parse_args()
    all_questions(args.llm_name)
