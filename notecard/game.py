#!/usr/bin/env python3
"""Run the game!"""

import time
from pathlib import Path
from random import shuffle

import pygame

from .conductor import Conductor
from .converters import frequency_to_nearest_note
from .mic_monitor import MicMonitor

BASE_DIR = Path(__file__).parent
UI_IMAGES = BASE_DIR / "images" / "ui"
WHITE = pygame.Color(255, 255, 255)
WIDTH = 800
HEIGHT = 600
GUESS_TIME = 10

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
SCREEN.fill(WHITE)

if __name__ == "__main__":
    my_concertina = Path("concertina/30button/jeffries_cg")
    conductor = Conductor(my_concertina)
    mic = MicMonitor()

    pygame.init()
    running = 1
    welcome_img = pygame.image.load(UI_IMAGES / "welcome.png")
    notfound_img = pygame.image.load(UI_IMAGES / "notfound.png")

    SCREEN.blit(welcome_img, (0, 0))
    pygame.display.flip()
    pygame.display.set_caption("NoteCard!")
    pygame.display.update()

    while running:
        with mic.start():
            time.sleep(2)
            notes = conductor.get_notes_list()
            shuffle(notes)

            for note in notes:
                test_note = note.name.split("/")[0]  # only testing on sharps
                try:
                    note_img = pygame.image.load(note.transcription)
                except FileNotFoundError:
                    print(f"Need to make note {note.name}!")
                    # note_img = notfound_img
                    continue

                SCREEN.blit(note_img, (0, 0))
                pygame.display.flip()
                pygame.display.update()

                start = time.time()
                current_freq = mic.get_currently_loudest_frequency()
                current_note = frequency_to_nearest_note(current_freq)[0]
                while time.time() - start < GUESS_TIME:
                    if current_note.split("/")[0] == test_note:
                        break
                    time.sleep(0.1)  # check every 10th of a second
                    current_freq = mic.get_currently_loudest_frequency()
                    current_note = frequency_to_nearest_note(current_freq)[0]
                else:
                    SCREEN.blit(pygame.image.load(note.fingering), (0, 0))
                    pygame.display.flip()

                    # make them play the note to continue
                    current_freq = mic.get_currently_loudest_frequency()
                    current_note = frequency_to_nearest_note(current_freq)[0]
                    while current_note.split("/")[0] != test_note:
                        time.sleep(0.1)
                        current_freq = mic.get_currently_loudest_frequency()
                        current_note = frequency_to_nearest_note(current_freq)[0]
        running = 0
    pygame.quit()
