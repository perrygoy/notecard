#!/usr/bin/env python3
"""Run the game!"""

import logging
from pathlib import Path
from random import shuffle

import pygame

from .conductor import Conductor
from .mic_monitor import MicMonitor

BASE_DIR = Path(__file__).parent
UI_IMAGES = BASE_DIR / "images" / "ui"
WHITE = pygame.Color(255, 255, 255)
BLACK = pygame.Color(0, 0, 0)
WIDTH = 800
HEIGHT = 600
GUESS_TIME = 5

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
SCREEN.fill(WHITE)

if __name__ == "__main__":
    my_concertina = Path("concertina/30button/jeffries_cg")
    conductor = Conductor(my_concertina)
    mic = MicMonitor()

    pygame.init()
    pygame.font.init()
    FONT = pygame.font.Font("freesansbold.ttf", 32)

    running = 1
    welcome_img = pygame.image.load(UI_IMAGES / "welcome.png")
    notfound_img = pygame.image.load(UI_IMAGES / "notfound.png")

    SCREEN.blit(welcome_img, (0, 0))
    pygame.display.flip()
    pygame.display.set_caption("NoteCard!")
    pygame.display.update()

    while running:
        with conductor.listening():
            notes = conductor.get_notes_list()
            shuffle(notes)

            for note in notes:
                try:
                    note_img = pygame.image.load(note.transcription)
                except FileNotFoundError:
                    logging.warn(f"Need to make note {note.name}!")
                    continue

                text = FONT.render(note.name, True, BLACK, WHITE)  # noqa: FBT003

                speech_bubble = text.get_rect()
                speech_bubble.center = (WIDTH - 100, HEIGHT - 50)
                SCREEN.blit(note_img, (0, 0))
                SCREEN.blit(text, speech_bubble)
                pygame.display.flip()
                pygame.display.update()

                if not conductor.hears_the_note(note.name, GUESS_TIME):
                    SCREEN.blit(pygame.image.load(note.fingering), (0, 0))
                    pygame.display.flip()

                    conductor.wait_for_note(note.name)

        running = 0
    pygame.quit()
