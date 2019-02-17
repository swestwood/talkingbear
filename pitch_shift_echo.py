#!/usr/bin/python
"""Listens to the user and pitch/duration shifts back the same audio

References:
https://stackoverflow.com/questions/40704026/voice-recording-using-pyaudio
https://pypi.org/project/SpeechRecognition/
https://realpython.com/python-speech-recognition/
pyaudio
"""

import random
import time
from aupyom import Sampler, Sound
import speech_recognition as sr

kRecordedWav = "recording.wav"


def main():
    initialize()
    while True:
        print "Press enter to talk."
        raw_input()
        record_from_mic()
        pitch_shift()


def initialize():
    global recognizer
    global mic
    recognizer = sr.Recognizer()
    mic = sr.Microphone()  # uses default system mic
    with mic as source:
        print "Adjusting for ambient noise... (please hush)"
        recognizer.adjust_for_ambient_noise(source, duration=2)


def record_from_mic():
    with mic as source:
        print "Speak! (silence to stop)"
        recording = recognizer.listen(source)
        print "Mimicking..."
        with open(kRecordedWav, "wb") as wav_output:
            wav_output.write(recording.get_wav_data())


def pitch_shift():
    sampler = Sampler()
    wav_file = kRecordedWav
    s1 = Sound.from_file(wav_file)
    sampler.play(s1)
    # Add random effects to be interesting
    while s1.playing:
        s1.pitch_shift = random.choice(
            [random.randint(-5, -3), random.randint(15, 20)])
        s1.stretch_factor = random.choice([.8, 1.2])
        time.sleep(.8)


def debug_microphones():
    mic_names = sr.Microphone.list_microphone_names()
    if len(mic_names) != 1:
        print "\n".join([(str(i) + ": " + mic_names[i]) for i in range(
            len(mic_names))])


if __name__ == "__main__":
    main()
