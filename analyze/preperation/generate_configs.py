import pandas as pd
import json
import random
import os
from itertools import combinations_with_replacement
import copy
from faker import Faker


QUESTIONS: list[tuple[str, str]] = [
    ("Tempolimit", "Auf allen Autobahnen soll ein generelles Tempolimit gelten."),
    ("Verteidigung", "Deutschland soll seine Verteidigungsausgaben erhöhen."),
    (
        "Jugentiche",
        "Bei Bundestagswahlen sollen auch Jugendliche ab 16 Jahren wählen dürfen.",
    ),
    ("Windenergie", "Die Förderung von Windenergie soll beendet werden."),
    (
        "Miete",
        "Die Möglichkeiten der Vermieterinnen und Vermieter, Wohnungsmieten zu erhöhen, sollen gesetzlich stärker begrenzt werden.",
    ),
]

# All unique vote combinations (pairs)
PARTIES = [
    "Die Linke",
    "SPD",
    "Bündnis 90/Die Grünen",
    "FDP",
    "CDU/CSU",
    "AfD",
    "keine Partei",
]

BASE_CONFIG = {
    "experiment": {
        "scenario": "Du diskutierst über die Aussage: {QUESTION}.",
        "survey_questions": [
            {
                "id": "intro",
                "iterations": "always",
                "question": "Von einer Scala von 0 bis 10 wie sehr stimmst du der Aussage zu: {QUESTION} Antwote nur mit einer Zahl.",
            }
        ],
    },
    "host": {"class": "Round Robin Host", "start_person_index": 0},
    "persons": [
        # Will be overwritten below
    ],
    "endType": {"class": "iteration", "max_num_msgs": 20},
}


def sanitize_filename(s) -> str:
    """Replace or remove problematic characters for filenames."""
    return (
        str(s).replace("/", "_").replace("\\", "_").replace(" ", "_").replace(":", "_")
    )


def random_male_name(fake: Faker) -> str:
    """Return a random German male first name."""
    male_name = fake.name_male()
    return cleanup(male_name)


def random_female_name(fake: Faker) -> str:
    """Return a random German female first name."""
    female_name = fake.name_female()
    return cleanup(female_name)


def cleanup(name: str) -> str:
    name = name.removesuffix("B.A.")
    name = name.removesuffix("B.Sc.")
    name = name.removesuffix("B.Eng.")
    name = name.removesuffix("MBA.")

    name = name.removeprefix("Ing. ")
    name = name.removeprefix("Prof. ")
    name = name.removeprefix("Univ.Prof. ")
    name = name.removeprefix("Dipl.-Ing. ")
    name = name.removeprefix("Dr. ")
    return name.strip()


def file_directory() -> str:
    """Return the directory of the current script."""

    return os.path.dirname(os.path.abspath(__file__))


def create_persons_for_json(
    vote: tuple[str, str], person: tuple, names: tuple[str, str]
) -> list[dict]:

    p1, p2 = vote
    person1, person2 = person
    name1, name2 = names

    return [
        {
            "class": "person_open_router_completion",
            "name": name1,
            "background_story": person1["prompt"],
            "party": p1,
        },
        {
            "class": "person_open_router_completion",
            "name": name2,
            "background_story": person2["prompt"],
            "party": p2,
        },
    ]


def create_names(fake: Faker, person1, person2) -> tuple[str, str]:

    name1 = ""
    name2 = ""
    while name1 == name2:
        name1 = (
            random_female_name(fake)
            if person1.get("female") == "weiblich"
            else random_male_name(fake)
        )
        name2 = (
            random_female_name(fake)
            if person2.get("female") == "weiblich"
            else random_male_name(fake)
        )

    return name1, name2


def get_persons_from_df(
    df: pd.DataFrame, p1: str, p2: str, random_state: int
) -> tuple[pd.Series, pd.Series]:
    """Get two random persons from the DataFrame based on their vote."""

    print(f"Selecting persons for parties: {p1} and {p2}")
    person1 = df[df["vote"] == p1].sample(1, random_state=random_state).iloc[0]
    person2 = df[df["vote"] == p2].sample(1, random_state=random_state + 1).iloc[0]

    # Ensure person1 and person2 are not the same
    while person1.equals(person2):
        random_state += 1
        person1 = df[df["vote"] == p1].sample(1, random_state=random_state).iloc[0]
        person2 = df[df["vote"] == p2].sample(1, random_state=random_state + 1).iloc[0]

    return person1, person2


def adding_scenario_to_config(config: dict, question: str) -> dict:
    """Add scenario and survey questions to the config."""
    experiment = config.get("experiment", {})

    # Dynamically replace {QUESTION} in scenario
    if "scenario" in experiment:
        experiment["scenario"] = experiment["scenario"].replace("{QUESTION}", question)

    # Update survey questions
    if "survey_questions" in experiment:
        for q in experiment["survey_questions"]:
            if "question" in q:
                q["question"] = q["question"].replace("{QUESTION}", question)

    config["experiment"] = experiment
    return config


def create_dir_and_save_config(
    config: dict,
    question_index: int,
    p1: str,
    p2: str,
    iteration: int,
) -> None:
    """Create directory for the config and save it as a JSON file."""
    safe_p1 = sanitize_filename(p1)
    safe_p2 = sanitize_filename(p2)

    combo_dir = os.path.join(
        f"config", f"question_{question_index}", f"{safe_p1}-{safe_p2}"
    )
    os.makedirs(combo_dir, exist_ok=True)
    filename = f"config_{iteration}.json"
    filepath = os.path.join(combo_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":

    random_state = 42
    random.seed(random_state)
    fake = Faker("de_DE")
    fake.seed_instance(random_state)

    # Load DataFrame from same directory as this script "ZA6835_v2-0-0.csv"
    csv_path = os.path.join(file_directory(), "ZA6835_v2-0-0.csv")

    df = pd.read_csv(csv_path, sep=";")

    # Ensure required columns exist
    assert "prompt" in df.columns and "vote" in df.columns

    vote_combinations = list(combinations_with_replacement(PARTIES, 2))

    for question_index, question in enumerate(QUESTIONS):
        random_state = 42
        random.seed(random_state)
        fake.seed_instance(random_state)
        # Reset random state for each question
        # This ensures that the same persons are selected for each question
        # but different combinations of persons are generated for each question

        print(f"Generating configs for question {question_index + 1}: {question[0]}")
        for party1, party2 in vote_combinations:

            for iteration in range(0, 10):
                random_state += 1

                person1, person2 = get_persons_from_df(df, party1, party2, random_state)
                names = create_names(fake, person1, person2)
                persons = create_persons_for_json(
                    vote=(party1, party2), person=(person1, person2), names=names
                )

                config = copy.deepcopy(BASE_CONFIG)

                config["persons"] = persons

                question_headline = question[0]
                question_text = question[1]

                config = adding_scenario_to_config(config, question_text)

                create_dir_and_save_config(
                    config, question_index, party1, party2, iteration
                )
