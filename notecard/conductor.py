"""Responsible for showing a note and verifying the right one was played."""

import json
import logging
import time
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from .converters import frequency_to_nearest_note
from .mic_monitor import MicMonitor

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
        self.mic = MicMonitor()

    @contextmanager
    def listening(self) -> Generator:
        """Listen to the user's performance."""
        with self.mic.start():
            yield

    def hears_the_note(self, note_name: str, guess_time: int | None = None) -> bool:
        """Wait for a note to be played.

        Args:
            note_name: the name of the note, e.g. "A#4/Bb4".
            guess_time: how long to wait. Default is None, which will wait
                until the note is played.

        Returns:
            bool: True if the note was heard, False if not.
        """
        start = time.time()
        current_freq = self.mic.get_currently_loudest_frequency()
        current_note = frequency_to_nearest_note(current_freq)[0]
        while current_note != note_name:
            logging.debug(f"Listening for {note_name}, hearing {current_note}")
            if guess_time is not None and time.time() - start > guess_time:
                return False
            time.sleep(0.1)  # check every 10th of a second
            current_freq = self.mic.get_currently_loudest_frequency()
            current_note = frequency_to_nearest_note(current_freq)[0]

        return True

    wait_for_note = hears_the_note

    def get_notes_list(self) -> list[Note]:
        """Get a full list of notes for the instrument."""
        notes = []
        for note in self.instrument_config["range"]:
            for accidental in note.lower().split("/"):
                filename = f"{accidental}.png"
                notes.append(
                    Note(
                        note,
                        NOTES_IMAGES / filename,
                        self.instrument_images_dir / filename,
                    )
                )

        return notes
