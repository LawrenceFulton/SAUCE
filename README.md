# SAUCE 🍝: Synchronous and Asynchronous User-Customizable Environment for Multi-Agent LLM Interaction

The system we are developing aims to facilitate the execution and replication of experiments in the fields of Social Psychology and Behavioral Economics, utilizing LLM (Large language model) as participant.
Our goal is to create an advanced experimental system that enables researchers to conduct and reproduce experiments with ease, specifically focusing on the domains of Social Psychology and Behavioral Economics. By leveraging LLM, we aim to reproduce experiment result using those LLMs.

## Requirements

- python >= 3.10
- basic requirements are in `requirements_law.txt`

## Installation

```bash
pip install -r requirements_law.txt
```

## Thesis Workflow

This section outlines the specific steps to reproduce the experiments conducted for the thesis.

### 1. Data Preparation

1.  **Download Data**: Download the dataset **ZA6835** from GESIS: [https://search.gesis.org/research_data/ZA6835](https://search.gesis.org/research_data/ZA6835).
2.  **Place Data**: Move the downloaded files into the `analyze/preperation/` directory.
3.  **Preprocess**: Run the notebook `analyze/preperation/stata_to_csv_2021.ipynb`. This script reads the GESIS data and preprocesses it into a CSV format suitable for configuration generation.

### 2. Configuration Generation

Before running experiments, you must generate the configuration files that define the agents and scenarios.

1.  **Select Model Type**: Open `analyze/preperation/generate_configs.py`.
    *   Set the `"PERSON_TYPE"` attribute to either:
        *   `"person_open_router_completion"` (for OpenRouter models)
        *   `"person_vllm"` (for local vLLM models)
2.  **Generate Configs**: Run the script:
    ```bash
    python analyze/preperation/generate_configs.py
    ```
    This will populate the `config/` directory with the experimental setups.

### 3. Running Experiments

You can run experiments using either OpenRouter or a local vLLM server.

#### Option A: Using vLLM (Local)

1.  **Configure Model**: Open `persons/person_vllm.py`.
    *   Adjust the default value of `self.model` in the `__init__` method to match the model you intend to run (e.g., `"openai/gpt-oss-120b"` or `"mistralai/Mistral-Small..."`).
2.  **Run Script**: Use one of the provided SLURM shell scripts to start the vLLM server and run the iterations:
    *   `sbatch vllm_meta.sh` (for Llama models)
    *   `sbatch vllm_mistral.sh` (for Mistral models)
    *   `sbatch vllm_openAI.sh` (for GPT-OSS models)

    *Note: These scripts automatically call `run_iterations.py` with the appropriate `--llm-name` argument.*

#### Option B: Using OpenRouter / Direct Execution

1.  **Configure Model**: Open `persons/person_open_router_completion.py`.
    *   Adjust the `MODEL_NAME` class attribute to match the model you intend to run (e.g., `"openai/gpt-4o-mini"`, `"google/gemini-2.0-flash-001"`, etc.).

2.  **Run Script**:
    If you are not using vLLM or want to run `run_iterations.py` directly:

    ```bash
    python run_iterations.py --llm-name <YOUR_LLM_NAME>
    ```

### 4. Analysis

After the experiments are complete, the results will be saved in the respective configuration folders. You can analyze the results using the notebook:
*   `analyze/lmm.ipynb`

## Sanity Check Workflow

To validate the model's responses against human judgment, a sanity check process was performed.

1.  **Preprocess Data**:
    Run the preprocessing script to aggregate survey questions and model answers from the experiment logs into a single JSONL file.
    ```bash
    python analyze/sanity_check_preprocess.py
    ```
    This generates a file (e.g., `preprocessed_out_41-mini.jsonl`) containing the data to be annotated.

2.  **Human Annotation (Google Colab)**:
    *   The notebook `analyze/sanity_check_colab.ipynb` was hosted on Google Colab.
    *   It imports the preprocessed data and presents questions to human annotators.
    *   Annotators provide their own answers based on the same prompts given to the model.
    *   **Output**: The results are exported as `analyze/Data collection.csv`.

3.  **Sanity Check Analysis**:
    Run the local analysis notebook to compare human vs. model performance.
    *   Open `analyze/sanity_check_analysis.ipynb`.
    *   This notebook reads `analyze/Data collection.csv` and calculates metrics like Mean Absolute Error (MAE) and performs statistical tests (Wilcoxon signed-rank test).

## Basic Usage (CLI)

For running individual configurations manually:

```bash
python main.py PATH_TO_CONFIG_FILE
```

**Arguments:**

```text
usage: SAUCE [-h] [-o OUTPUT] [--json | --no-json] [--output-json OUT_JSON] [-c | --console | --no-console] [--output-log OUT_LOG] [--batch-mode | --no-batch-mode | -bm]
             [-v | --verbose | --no-verbose]
             config

positional arguments:
  config                what config to run

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Where to save the experiment output
  --json, --no-json     boolean field indicting rather saved or not to save a json version of the logs (default: False)
  --output-json OUT_JSON
                        File where to save the json form of the raw logs
  -c, --console, --no-console
                        Enable output to std output (default: True)
  --output-log OUT_LOG  Where to save the created log
  --batch-mode, --no-batch-mode, -bm
                        Change the running exp to use Batch mode person (default: False)
  -v, --verbose, --no-verbose
```

## Software Design

### Classes

- <u><b>Person:</b></u> An abstract class representing a participant utilizing LLM in the experiment. It encapsulates the common attributes and behaviors of participants.
- <u><b>Session Room:</b></u> Represents the physical or virtual space where the experiments take place. It serves as the environment where participants interact with each other.
- <u><b>Host:</b></u> An abstract representation of the experiment conductor who guides and manages the interactions between participants. It determines the rules and conditions of the experiment and controls the timing and sequencing of participant interactions.
- <u><b>EndType:</b></u> An abstract representation of the criteria or condition that determines the conclusion or termination of the experiment. It defines what constitutes the end of the experiment and triggers any necessary actions or data collection.
- <u><b>Experiment:</b></u> This class serves as a container for the experiment blueprint. It encapsulates the experimental design, instructions, stimuli, and any other relevant information needed for conducting the experiment.
