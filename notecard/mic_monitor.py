"""Monitors the microphone, listening for any notes that might be going on.

Typical usage looks like:

    m = MicMonitor()
    m.start()
    m.get_currently_loudest_frequency()
    # maybe do something with that? Maybe get some more??
    m.stop()
"""

import copy
from collections.abc import Generator, Mapping
from contextlib import contextmanager
from typing import TYPE_CHECKING

import numpy as np
import sounddevice  # noqa: F401  # it's needed for pyaudio to work
from pyaudio import PyAudio, paContinue, paInt16

if TYPE_CHECKING:
    from pyaudio import Stream


class MicMonitor:
    """Monitors the mic, doing analysis and stuff."""

    SAMPLING_RATE = 48000  # mac hardware: 44100, 48000, 96000
    CHUNK_SIZE = 1024  # number of samples
    BUFFER_TIMES = 50  # buffer length = CHUNK_SIZE * BUFFER_TIMES
    ZERO_PADDING = 3  # times the buffer length
    NUM_HPS = 3  # Harmonic Product Spectrum
    FREQ_FLOOR = 60  # lowest note to listen for

    def __init__(self) -> None:
        self.buffer = np.zeros(self.CHUNK_SIZE * self.BUFFER_TIMES)
        self.hanning_window = np.hanning(len(self.buffer))
        self.audio = PyAudio()
        self.mic: Stream | None = None

    def _buffer_callback(
        self, in_data: bytes | None, _: int, __: Mapping[str, float], ___: int
    ) -> tuple[bytes | None, int]:
        """Callback function for the PyAudio stream; appends recording to buffer."""
        if in_data is not None:
            data = np.frombuffer(in_data, dtype=np.int16)
            self.buffer[: -self.CHUNK_SIZE] = self.buffer[self.CHUNK_SIZE :]
            self.buffer[-self.CHUNK_SIZE :] = data

        return (in_data, paContinue)

    @contextmanager
    def start(self) -> Generator:
        """Start listening to the microphone."""
        self.mic = self.audio.open(
            format=paInt16,
            channels=1,
            rate=self.SAMPLING_RATE,
            input=True,
            frames_per_buffer=self.CHUNK_SIZE,
            stream_callback=self._buffer_callback,
        )
        try:
            yield
        finally:
            self.stop()

    def get_currently_loudest_frequency(self) -> str:
        """Get the frequency of the loudest sound the mic can currently hear.

        This approach was lifted from the audio_analyzer.py file at
        https://github.com/TomSchimansky/GuitarTuner
        """
        # apply the fourier transformation on the whole buffer
        # (with zero-padding + hanning window)
        magnitude_data = abs(
            np.fft.fft(
                np.pad(
                    self.buffer * self.hanning_window,
                    (0, len(self.buffer) * 3),
                    "constant",
                )
            )
        )
        # only use the first half of the fft output data
        magnitude_data = magnitude_data[: int(len(magnitude_data) / 2)]

        # multiply data by itself with different scalings (Harmonic Product Spectrum)
        magnitude_data_orig = copy.deepcopy(magnitude_data)
        for i in range(2, self.NUM_HPS + 1, 1):
            hps_len = int(np.ceil(len(magnitude_data) / i))
            magnitude_data[:hps_len] *= magnitude_data_orig[
                ::i
            ]  # multiply every i element

        # get the corresponding frequency array
        frequencies = np.fft.fftfreq(
            int((len(magnitude_data) * 2) / 1), 1.0 / self.SAMPLING_RATE
        )

        # set magnitude of all frequencies below 60Hz to zero
        for i, freq in enumerate(frequencies):
            if freq > self.FREQ_FLOOR:
                magnitude_data[: i - 1] = 0
                break

        # return the frequency of the loudest sound in the buffer
        return round(frequencies[np.argmax(magnitude_data)], 2)

    def stop(self) -> None:
        """Stop listening to the microphone."""
        if self.mic is None:
            # our work is done.
            return

        self.mic.stop_stream()
        self.mic.close()
        self.mic = None
