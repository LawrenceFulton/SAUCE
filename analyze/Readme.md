# Analyze Folder

This directory contains scripts and notebooks for analyzing experiment results and preparing data.

## Python Scripts

### `sanity_check_preprocess.py`
This script preprocesses data for the sanity check analysis. It iterates through configuration or output JSON files, extracts survey question entries, and prepares them for further analysis (likely in the sanity check notebooks). It handles directory resolution and JSON parsing.

### `preperation/generate_configs.py`
This script generates the configuration JSON files required to run the experiments. It defines the survey questions (e.g., Tempolimit, Verteidigung), political parties, and the base experiment structure. It creates combinations of parameters and saves them as JSON files to be used by the main experiment runner.

## Jupyter Notebooks

### `lmm.ipynb`
**Thesis Data Analysis: Opinion Dynamics & Linear Mixed Models**
This notebook performs the core statistical analysis for the thesis. It processes simulation logs to analyze:
- **Opinion Shifts:** How agent opinions change over time during discussions.
- **Party Alignment:** The correlation between agent opinions and official party stances.
- **Convergence:** Analysis of variance to determine if opinions converge.
It uses Linear Mixed Models (LMM), Spearman Correlation, and Cohen's f^2 effect size.

### `sanity_check_analysis.ipynb`
This notebook analyzes the results of the sanity check. It reads data from `Data collection.csv` and calculates the Mean Absolute Error (MAE) between user answers and model answers. It also performs statistical tests (Wilcoxon signed-rank test) to check for significant differences and groups errors by question.

### `sanity_check_colab.ipynb`
**Interactive Sanity Check**
Designed to be run in Google Colab, this notebook allows for interactive exploration of the simulated LLM responses. It downloads the dataset, loads it, and presents random questions to the user to compare their answers with the LLM's generated answers. It handles Google Drive authentication and data fetching.

### `preperation/stata_to_csv_2021.ipynb`
**Data Preparation: Stata to CSV**
This notebook processes the raw survey data (ZA6835_v2-0-0 from GESIS). It reads the Stata file (`.dta`), filters for specific field start dates, cleans missing values, and recodes demographic variables (age, gender, education) to prepare the data for use in the project.

