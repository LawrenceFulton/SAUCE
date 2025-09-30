from __future__ import annotations

import json
import os
import random
import sys
import textwrap
from pathlib import Path
from typing import Dict, List


def discover_model_files(config_root: Path, model_prefix: str) -> List[str]:
    """Return all JSON files under config_root matching the model prefix."""

    candidates: List[str] = []
    for root, _, files in os.walk(config_root):
        for filename in files:
            if not filename.endswith(".json"):
                continue
            if model_prefix and not filename.startswith(model_prefix):
                continue
            candidates.append(os.path.join(root, filename))
    return candidates


def pretty_print_prompt(prompt_messages: List[Dict[str, str]]) -> None:
    """Print the conversation prompt with simple formatting."""

    for message in prompt_messages:
        role = message.get("role", "?").upper()
        content = message.get("content", "").strip()
        wrapped = textwrap.fill(content, width=100, subsequent_indent="    ")
        print(f"{role}: {wrapped}")


def compare_answers(user_answer: str, model_answer: str) -> None:
    """Display both answers and, when possible, a numeric difference."""

    print(f"\nYour answer:  {user_answer}")
    print(f"LLM answer:   {model_answer}")

    try:
        user_val = float(user_answer)
        model_val = float(model_answer)
    except ValueError:
        return

    diff = abs(user_val - model_val)
    print(f"Difference:   {diff:.2f}\n")


def resolve_config_dir() -> Path:
    """Locate the config directory in source or frozen deployments."""

    candidates = []

    script_dir = Path(__file__).resolve().parent
    candidates.append(script_dir / "config")
    candidates.append(script_dir.parent / "config")

    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir:
        bundle_path = Path(bundle_dir)
        candidates.append(bundle_path / "config")

    for candidate in candidates:
        if candidate.is_dir():
            return candidate

    searched = "\n".join(str(path) for path in candidates)
    raise FileNotFoundError(f"Config directory not found. Searched:\n{searched}")


def main() -> None:
    model_input = input("Enter model prefix (default 'out_41-mini'): ").strip()
    if not model_input or model_input.lower().startswith("default"):
        model_name = "out_41-mini"
    else:
        model_name = model_input
    model_name = model_name.strip("'\"")

    rounds_input = input("Enter number of rounds (e.g., 5): ").strip()
    if not rounds_input:
        n_rounds_str = "5"
    elif rounds_input.lower().startswith("default"):
        n_rounds_str = rounds_input.split()[-1]
    else:
        n_rounds_str = rounds_input
    n_rounds = int(n_rounds_str.strip("'\""))

    config_path = resolve_config_dir()

    candidate_files = discover_model_files(config_path, model_name)
    if not candidate_files:
        raise FileNotFoundError(
            f"No JSON files starting with '{model_name}' found under {config_path}"
        )

    print(f"Discovered {len(candidate_files)} matching JSON files. Let's compare answers!\n")

    for round_num in range(1, n_rounds + 1):
        chosen_path = random.choice(candidate_files)
        with open(chosen_path, "r", encoding="utf-8") as f:
            model_data = json.load(f)

        survey_questions = model_data.get("survey_question") or []
        if not survey_questions:
            print(f"[{round_num}] Skipping {chosen_path} (no survey questions)")
            continue

        selected_question = random.choice(survey_questions)
        chat_entry = selected_question.get("chat_entry", {})
        prompt_messages = chat_entry.get("prompt", [])
        model_answer = str(chat_entry.get("answer", "")).strip()

        print("=" * 80)
        print(f"Round {round_num}")
        print(f"Source file: {chosen_path}")
        print(
            f"Question: {selected_question.get('question_content', 'Unknown question')}"
        )
        print(f"Iteration: {selected_question.get('iteration', 'n/a')}")
        entity = chat_entry.get("entity", {})
        if entity:
            print(
                f"Respondent: {entity.get('name', 'n/a')} ({entity.get('person_type', 'unknown')})"
            )
        print("-- Prompt --")
        pretty_print_prompt(prompt_messages)

        user_answer = input("\nYour answer: ").strip()
        compare_answers(user_answer, model_answer)

    print("All rounds completed.")


if __name__ == "__main__":
    main()
        



