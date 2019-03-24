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
import pydub
import pydub.playback
import random
import speech_recognition as sr
import time
import threading
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.cloud import texttospeech

kTalkFile = "generated_talk.mp3"
mic = None
recognizer = None
language = "en"
filler_thread = None
kDoTheStupidJavascriptThing = False  # Only enable if on a laptop with
                                     # unresolvable protoc version conflicts

ENV = "mac"

if ENV == "linux":
    kSystemPlayer = "mpg321"
    kNodePath = "/home/pi/.nvm/versions/node/v11.11.0/bin/node"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
        "/home/pi/bear/talkingbear-9bfef5bb7338.json")
else:
    kSystemPlayer = "afplay"  # alt: mplayer, mpg123, etc
    kNodePath = "/usr/local/bin/node"
    # Or set it up in bash profile
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
        "/Users/lillian/Desktop/talkingbear-master/talkingbear-9bfef5bb7338.json")


def get_voice_details(voicetype):
    print voicetype
    if voicetype == 2:
        return {
            "language_code": 'en-GB',
            "gender": texttospeech.enums.SsmlVoiceGender.FEMALE,
            "name": "en-GB-Standard-A",
            "pitch": 6.4,
            "speaking_rate": 0.7
        }
    elif voicetype == 3:
        return {
            "language_code": 'de-DE',
            "gender": texttospeech.enums.SsmlVoiceGender.FEMALE,
            "name": "de-DE-Standard-A",
            "pitch": 2.40,
            "speaking_rate": 0.9
        }
    elif voicetype == 4:
        return {
            "language_code": 'ja-JP',
            "gender": texttospeech.enums.SsmlVoiceGender.FEMALE,
            "name": "ja-JP-Standard-A",
            "pitch": 2.40,
            "speaking_rate": 1.23
        }
    return {
        "language_code": 'en-AU',
        "gender": texttospeech.enums.SsmlVoiceGender.FEMALE,
        "name": "en-AU-Standard-C",
        "pitch": 6.0,
        "speaking_rate": 0.9
    }

def main():
    initialize()
    # raw_input("Press enter to start.")
    if ENV == "linux":
        voicetype = 1
    else:
        voicetype = int(raw_input("Which voice? (1 = Aussie, 2 = UK, 3 = German, 4 = Chinese) "))
    while True:
        text = record_from_mic(voicetype)
        if text and text.lower() == "new voice":
            voicetype = random.choice([num for num in range(1, 5) if num != voicetype])
            print "Chose new voice."
            continue
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

def play_filler(voicetype):
    global filler_thread
    def play_filler_sound():
        print "In thread"
        #sound = pydub.AudioSegment.from_mp3("fillers/filler0.mp3")
        #sound = pydub.AudioSegment.from_mp3("fillers/filler%d.mp3" % random.randint(0, 4))
        sound = pydub.AudioSegment.from_mp3("fillers/filler%d.mp3" % (voicetype - 1))
        pydub.playback.play(sound)

    filler_thread = threading.Thread(target=play_filler_sound)
    filler_thread.start()

def js_text_to_speech_deprecated(text, voicetype):
    # Calls out to a JS file because there's a dumb protoc versioning issue
    # on this laptop with running Google's Python text to speech library
    t = rounded_time()
    subprocess.Popen([kNodePath, "talk.js", language, voicetype, text]).wait()
    print "--- timing to speech: " + str(rounded_time() - t) + " ---"
    subprocess.Popen([kSystemPlayer, kTalkFile]).wait()

def text_to_speech(text, voicetype):
    t = rounded_time()
    set_language(text);
    print "language: " + str(language)
    print "voicetype: " + str(voicetype)
    print "text: "+ str(text)
    voice_details = get_voice_details(voicetype)
    print voice_details["name"]
    if kDoTheStupidJavascriptThing:
        js_text_to_speech_deprecated(text, voicetype)
        return

    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    if not text:
        return
    synthesis_input = texttospeech.types.SynthesisInput(text=(text or "mumble mumble"))

    voice = texttospeech.types.VoiceSelectionParams(
        language_code=voice_details["language_code"],
        name=voice_details["name"],
        ssml_gender=voice_details["gender"])

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3,
        pitch=voice_details["pitch"],
        speaking_rate=voice_details["speaking_rate"]
        )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(synthesis_input, voice, audio_config)
    print "--- timing to speech: " + str(rounded_time() - t) + " ---"
    t = rounded_time()
    # TODO we could probably play this directly without saving to mp3
    # The response's audio_content is binary.
    with open(kTalkFile, 'wb') as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')
    print "--- written to file: "  + str(rounded_time() - t) + " ---"
    if filler_thread:
        filler_thread.join()  # wait for the filler filler_thread
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

def record_from_mic(voicetype):
    with mic as source:
        print "Speak! (silence to stop)"
        recording = recognizer.listen(source, None, 3)
        t = rounded_time()
        print "Mimicking..."
        # Kick off a filler sound while we compute
        # play_filler(voicetype)
        try:
            # text = recognizer.recognize_sphinx(recording)
            text = recognizer.recognize_google(recording)
        except sr.RequestError:
            # Unable to reach API
            text = "Woof woof woof!"
            print text
        except sr.UnknownValueError:
            # Unable to transcribe text
            # text = "Mumble mumble mumble."
            text = ""
            print "could not identify"
        print "--- time to text: " + str(rounded_time() - t) + " ---"
        return text


def debug_microphones():
    mic_names = sr.Microphone.list_microphone_names()
    if len(mic_names) != 1:
        print "\n".join([(str(i) + ": " + mic_names[i]) for i in range(
            len(mic_names))])


if __name__ == "__main__":
    main()
