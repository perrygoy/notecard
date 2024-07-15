"""Useful conversion functions between notes and numbers."""

import numpy as np

A4_FREQUENCY = 440
A4_NUMBER = 69
ACCIDENTAL_TOLERANCE = 5
NOTE_LETTERS = [
    "C{octave}",
    "C#{octave}/Db{octave}",
    "D{octave}",
    "D#{octave}/Eb{octave}",
    "E{octave}",
    "F{octave}",
    "F#{octave}/Gb{octave}",
    "G{octave}",
    "G#{octave}/Ab{octave}",
    "A{octave}",
    "A#{octave}/Bb{octave}",
    "B{octave}",
]


def frequency_to_note_number(freq: float) -> int:
    """Get the note number from the frequency (e.g. 440 -> 69)."""
    return round(12 * np.log2(freq / A4_FREQUENCY) + A4_NUMBER)


def note_number_to_letter(number: int) -> str:
    """Get the letter of the note from its number."""
    return NOTE_LETTERS[int(round(number) % 12)].format(octave=int(number / 12) - 1)


def note_number_to_frequency(number: int) -> float:
    """Get the standard frequency of a note from its number."""
    return A4_FREQUENCY * 2.0 ** ((number - 69) / 12.0)


def frequency_to_nearest_note(freq: float) -> tuple[str, int]:
    """Get the nearest note to the given frequency.

    Also returned is whether the note was sharp (>0), flat (<0), or natural (0).

    Args:
        freq: the frequency to map to a note.

    Returns:
        tuple[str, int]: the note name and accidental
    """
    frequency = round(freq, 2)
    note_number = frequency_to_note_number(frequency)
    std_frequency = note_number_to_frequency(note_number)

    accidental = 0
    if frequency != std_frequency:
        if frequency > (std_frequency + ACCIDENTAL_TOLERANCE):
            accidental = 1
        elif frequency < (std_frequency - ACCIDENTAL_TOLERANCE):
            accidental = -1

    return (note_number_to_letter(note_number), accidental)
