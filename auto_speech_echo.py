#!/usr/bin/python
"""Listens to the user, identifies the text, then vocalizes back the same text.

References:
https://pypi.org/project/SpeechRecognition/
https://realpython.com/python-speech-recognition/
Explore text to speech voices - https://cloud.google.com/text-to-speech/
https://cloud.google.com/text-to-speech/docs/voices
https://cloud.google.com/text-to-speech/docs/create-audio
pyaudio
"""

import os
import subprocess
import time
import speech_recognition as sr

kSystemPlayer = "afplay"  # alt: mplayer, mpg123, etc
kNodePath = "/usr/local/bin/node"
kTalkFile = "generated_talk.mp3"
mic = None
recognizer = None
language = "en"

# Or set it up in bash profile
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
    "/Users/lillian/Desktop/talkingbear-master/talkingbear-9bfef5bb7338.json")


def main():
    initialize()
    # raw_input("Press enter to start.")
    voicetype = raw_input("Which voice? (1 = Aussie, 2 = UK, 3 = German, 4 = Chinese) ")
    while True:
        text = record_from_mic()
        text_to_speech(text, voicetype)


def initialize():
    global recognizer
    global mic
    
    recognizer = sr.Recognizer()

    mic = sr.Microphone()  # uses default system mic
    with mic as source:
        # always do this for 0.5-1 second
        print "Adjusting for ambient noise... (please hush)"
        recognizer.adjust_for_ambient_noise(source, duration=2)
        recognizer.pause_threshold = 0.2
        recognizer.non_speaking_duration = 0.2


def rounded_time():
    return round(time.time(), 1)


def text_to_speech(text, voicetype):
    # Calls out to a JS file because there's a dumb protoc versioning issue
    # on this laptop with running Google's Python text to speech library
    t = rounded_time()
    set_language(text);
    print "language: "+str(language)
    print "voicetype: "+str(voicetype)
    print "text: "+str(text)
    subprocess.Popen([kNodePath, "talk.js", language, voicetype, text]).wait()
    print "--- timing to speech: " + str(rounded_time() - t) + " ---"
    subprocess.Popen([kSystemPlayer, kTalkFile]).wait()

def set_language(text):
    global language
    if text.lower() == "spanish":
        language = "es";
    elif text.lower() == "english":
        language = "en";
    elif text.lower() == "german":
        language = "de";
    elif text.lower() == "slovak":
        language = "sk";
    elif text.lower() == "japanese":
        language = "ja";
    elif text.lower() == "chinese":
        language = "zh-CN";
    elif text.lower() == "french":
        language = "fr";

def record_from_mic():
    with mic as source:
        print "Speak! (silence to stop)"
        recording = recognizer.listen(source)
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
            print text
        except sr.UnknownValueError:
            # Unable to transcribe text
            text = "Mumble mumble mumble."
            print text
        print "--- time to text: " + str(rounded_time() - t) + " ---"
        return text


def debug_microphones():
    mic_names = sr.Microphone.list_microphone_names()
    if len(mic_names) != 1:
        print "\n".join([(str(i) + ": " + mic_names[i]) for i in range(
            len(mic_names))])


if __name__ == "__main__":
    main()
