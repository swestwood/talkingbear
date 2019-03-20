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
import io
import subprocess
import time
import pyaudio
import wave
import keyboard
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

kSystemPlayer = "afplay"  # alt: mplayer, mpg123, etc
kNodePath = "/usr/local/bin/node"
kTalkFile = "generated_talk.mp3"
language = "en"

# Or set it up in bash profile
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
    "/Users/lillian/Desktop/talkingbear-master/talkingbear-9bfef5bb7338.json")


def main():
    while True:
        record_from_mic()
        text_to_speech(speech_to_text())

def rounded_time():
    return round(time.time(), 1)

def text_to_speech(text):
    # Calls out to a JS file because there's a dumb protoc versioning issue
    # on this laptop with running Google's Python text to speech library
    t = rounded_time()
    set_language(text);
    subprocess.Popen([kNodePath, "talk.js", language, text]).wait()
    print "--- timing to speech: " + str(rounded_time() - t) + " ---"
    subprocess.Popen([kSystemPlayer, kTalkFile]).wait()

def speech_to_text():
    # Instantiates a client
    client = speech.SpeechClient()

    # Loads the audio into memory
    with io.open(WAVE_OUTPUT_FILENAME, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code='en-US', 
        audio_channel_count=2)

    # Detects speech in the audio file
    response = client.recognize(config, audio)
    return response.results[0].alternatives[0].transcript

def record_from_mic():
    print "Hold spacebar and talk!"
    while True:
        try:
            if keyboard.is_pressed(" "):
                break;
            else:
                pass
        except:
            break;

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
    print "Recording..."
    frames = []

    while keyboard.is_pressed(" "):
        data = stream.read(CHUNK)
        frames.append(data)

    print "Done recording."

    stream.stop_stream()
    stream.close()
    p.terminate()

    t = rounded_time()
    
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Kick off a filler sound while we compute
    subprocess.Popen([kSystemPlayer, "filler.mp3"])
        

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

if __name__ == "__main__":
    main()
