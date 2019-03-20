#!/usr/bin/python
"""Listens to the user, identifies the text, then vocalizes back the same text.

References:
https://pypi.org/project/SpeechRecognition/
https://realpython.com/python-speech-recognition/
Explore text to speech voices - https://cloud.google.com/text-to-speech/
https://cloud.google.com/text-to-speech/docs/voices
https://cloud.google.com/text-to-speech/docs/create-audio
"""

import os
import subprocess
import time
import speech_recognition as sr

IS_PI = True

kSystemPlayer = "mpg321" if IS_PI else "afplay" # alt: mplayer, mpg321, omxplayer etc
kNodePath = "/home/pi/.nvm/versions/node/v11.11.0/bin/node"
kTalkFile = "generated_talk.mp3"
mic = None
recognizer = None


# Or set it up in bash profile
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
    "/home/pi/bear/talkingbear-9bfef5bb7338.json")


def main():
    initialize()
    # raw_input("Press enter to start.")
    debug_microphones()
    while True:
        text = record_from_mic()
        text_to_speech(text)


def initialize():
    global recognizer
    global mic
    recognizer = sr.Recognizer()
    mic = sr.Microphone(device_index=2) if IS_PI else sr.Microphone()
    with mic as source:
        # always do this for 0.5-1 second
        print "Adjusting for ambient noise... (please hush)"
        recognizer.adjust_for_ambient_noise(source, duration=2)


def rounded_time():
    return round(time.time(), 1)


def text_to_speech(text):
    # Calls out to a JS file because there's a dumb protoc versioning issue
    # on this laptop with running Google's Python text to speech library
    t = rounded_time()
    subprocess.Popen([kNodePath, "talk.js", text]).wait()
    print "--- timing to speech: " + str(rounded_time() - t) + " ---"
    subprocess.Popen([kSystemPlayer, kTalkFile]).wait()


def record_from_mic():
    with mic as source:
        print "Speak! (silence to stop)"
        recording = recognizer.listen(source)
        # write audio to a WAV file to debug
        # with open("microphone-results.wav", "wb") as f:
        #     f.write(recording.get_wav_data())

        t = rounded_time()
        print "Mimicking..."
        # Kick off a filler sound while we compute
        subprocess.Popen([kSystemPlayer, "filler.mp3"])
        try:
            # text = recognizer.recognize_sphinx(recording)
            text = recognizer.recognize_google(recording)
        except sr.RequestError:
            # Unable to reach API
            text = "Woof woof woof!"
        except sr.UnknownValueError:
            # Unable to transcribe text
            text = "Mumble mumble mumble."
        print text
        print "--- time to text: " + str(rounded_time() - t) + " ---"
        return text


def debug_microphones():
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))


if __name__ == "__main__":
    main()
