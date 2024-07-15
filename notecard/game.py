#!/usr/bin/env python3
"""Run the game!"""

from pathlib import Path

from .conductor import Conductor

if __name__ == "__main__":
    my_concertina = Path("concertina/30button/jeffries_cg")
    conductor = Conductor(my_concertina)
    conductor.conduct()
