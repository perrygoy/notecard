"""Responsible for showing a note and verifying the right one was played."""

import json
from dataclasses import dataclass
from pathlib import Path
from random import choice

BASE_DIR = Path(__file__).parent
CONFIGS_PREFIX = BASE_DIR / "configs"
IMAGES_PREFIX = BASE_DIR / "images"
NOTES_IMAGES = IMAGES_PREFIX / "notes"
FINGERING_IMAGES = IMAGES_PREFIX / "instruments"


@dataclass
class Note:
    """Combine a note name and its image paths together."""

    name: str
    transcription: Path
    fingering: Path


class Conductor:
    """Conducts the game!

    Uses the chosen settings to play the note guessing game.
    """

    def __init__(self, instrument_path: Path) -> None:
        config_path = CONFIGS_PREFIX / instrument_path / "config.json"
        self.instrument_config = json.load(config_path.open())
        self.instrument_images_dir = FINGERING_IMAGES / instrument_path

    def announce(self, msg: str) -> None:
        """Say something to the user."""
        print(msg)  # noqa: T201

    def get_notes_list(self) -> list[Note]:
        """Get a full list of notes for the instrument."""
        notes = []
        for note in self.instrument_config["range"]:
            for accidental in note.lower().split("/"):
                filename = f"{accidental}.png"
                notes.append(
                    Note(
                        note, NOTES_IMAGES / filename, self.instrument_images_dir / filename
                    )
                )

        return notes
