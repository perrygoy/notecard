"""Responsible for showing a note and verifying the right one was played."""

import json
import time
from pathlib import Path
from random import sample

from .converters import frequency_to_nearest_note
from .mic_monitor import MicMonitor

BASE_DIR = Path(__file__).parent
CONFIGS_PREFIX = BASE_DIR / "configs"
IMAGES_PREFIX = BASE_DIR / "images"
NOTES_IMAGES = IMAGES_PREFIX / "notes"
GUESS_TIME = 5


class Conductor:
    """Conducts the game!

    Uses the chosen settings to play the note guessing game.
    """

    def __init__(self, instrument_path: Path) -> None:
        config_path = CONFIGS_PREFIX / instrument_path / "config.json"
        self.instrument_config = json.load(config_path.open())
        self.instrument_images_dir = IMAGES_PREFIX / instrument_path
        self.mic_monitor = MicMonitor()

    def announce(self, msg: str) -> None:
        """Say something to the user."""
        print(msg)  # noqa: T201

    def conduct(self) -> None:
        """Conduct the game!"""
        with self.mic_monitor.start():
            time.sleep(2)
            note_range = self.instrument_config["range"]
            for note in sample(note_range, k=len(note_range)):
                self.announce(f"Play a {note}, please!")
                start = time.time()
                current_freq = self.mic_monitor.get_currently_loudest_frequency()
                current_note = frequency_to_nearest_note(current_freq)[0]
                while time.time() - start < GUESS_TIME:
                    if current_note == note:
                        self.announce("Hooray!")
                        break
                    time.sleep(0.1)  # check every 10th of a second
                    current_freq = self.mic_monitor.get_currently_loudest_frequency()
                    current_note = frequency_to_nearest_note(current_freq)[0]
                else:
                    self.announce(
                        "Shucks, well i'd like to show you how,"
                        " but that's not implemented."
                    )
