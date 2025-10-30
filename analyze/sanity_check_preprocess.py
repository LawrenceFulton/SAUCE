from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterator, List, Optional


def resolve_config_dir(explicit_path: Optional[str] = None) -> Path:
    """Locate the config directory either via explicit path or relative defaults."""

    if explicit_path:
        candidate = Path(explicit_path).expanduser().resolve()
        if not candidate.is_dir():
            raise FileNotFoundError(f"Provided config path does not exist: {candidate}")
        return candidate

    script_dir = Path(__file__).resolve().parent
    default_candidates = [script_dir.parent / "config", script_dir / "config"]

    for candidate in default_candidates:
        if candidate.is_dir():
            return candidate

    searched = "\n".join(str(path) for path in default_candidates)
    raise FileNotFoundError(
        "Config directory not found. Provide --config-dir explicitly. Searched:\n" + searched
    )


def iter_survey_entries(config_root: Path, model_prefix: str) -> Iterator[Dict[str, object]]:
    """Yield flattened survey question entries for the chosen model prefix."""

    for json_path in sorted(config_root.rglob("*.json")):
        if model_prefix and not json_path.name.startswith(model_prefix):
            continue

        try:
            with json_path.open("r", encoding="utf-8") as fh:
                payload = json.load(fh)
        except json.JSONDecodeError as exc:
            print(f"Skipping {json_path}: invalid JSON ({exc})")
            continue

        survey_questions: List[Dict[str, object]] = payload.get("survey_question") or []
        if not survey_questions:
            continue

        relative_path = json_path.relative_to(config_root)

        for question in survey_questions:
            chat_entry = question.get("chat_entry", {}) if isinstance(question, dict) else {}
            prompt_messages = chat_entry.get("prompt", []) if isinstance(chat_entry, dict) else []
            entity = chat_entry.get("entity") if isinstance(chat_entry, dict) else None
            answer = chat_entry.get("answer", "") if isinstance(chat_entry, dict) else ""

            record: Dict[str, object] = {
                "source_file": str(relative_path),
                "model_prefix": model_prefix,
                "question_id": question.get("question_id"),
                "question_content": question.get("question_content"),
                "iteration": question.get("iteration"),
                "prompt_messages": prompt_messages,
                "entity": entity,
                "model_answer": answer,
            }

            # Attempt to capture prompt version info from filename, e.g. out_41-mini_v1_3.json
            parts = json_path.stem.split("_v", maxsplit=1)
            if len(parts) == 2:
                record["file_suffix"] = parts[1]

            yield record


def preprocess(config_root: Path, output_path: Path, model_prefix: str, overwrite: bool) -> int:
    """Run the preprocessing step and write JSON Lines output."""

    if output_path.exists() and not overwrite:
        raise FileExistsError(
            f"Output file already exists: {output_path}. Use --overwrite to replace it."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with output_path.open("w", encoding="utf-8") as out_f:
        for record in iter_survey_entries(config_root, model_prefix):
            out_f.write(json.dumps(record, ensure_ascii=False))
            out_f.write("\n")
            count += 1

    return count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preprocess survey questions for sanity_check into a single JSONL dataset."
    )
    parser.add_argument(
        "--config-dir",
        type=str,
        default=None,
        help="Path to the config directory (defaults to ../config relative to this script).",
    )
    parser.add_argument(
        "--model-prefix",
        type=str,
        default="out_41-mini",
        help="Model file prefix to include in the dataset.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(Path(__file__).with_name("preprocessed_out_41-mini.jsonl")),
        help="Destination JSON Lines file (default: preprocess script directory).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace the output file if it already exists.",
    )

    args = parser.parse_args()

    config_root = resolve_config_dir(args.config_dir)
    output_path = Path(args.output).expanduser().resolve()

    print(f"Scanning config directory: {config_root}")
    print(f"Writing merged dataset to: {output_path}")

    total = preprocess(config_root, output_path, args.model_prefix, args.overwrite)

    print(f"Done. Collected {total} survey entries.")


if __name__ == "__main__":  # pragma: no cover
    main()
