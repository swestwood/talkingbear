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
import pydub
import pydub.playback
import wave
import keyboard
import threading
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.cloud import texttospeech

CHUNK = 4096
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

kSystemPlayer = "mpg321"  # alt: mplayer, mpg321, etc
kNodePath = "/home/pi/.nvm/versions/node/v11.11.0/bin/node"
kTalkFile = "generated_talk.mp3"
language = "en"
filler_thread = None

# Or set it up in bash profile
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
    "/home/pi/bear/talkingbear-9bfef5bb7338.json")


def main():
    while True:
        text_to_speech(speech_to_text())

def rounded_time():
    return round(time.time(), 1)

# def text_to_speech_js(text):
#     # Calls out to a JS file because there's a dumb protoc versioning issue
#     # on this laptop with running Google's Python text to speech library
#     print text
#     t = rounded_time()
#     set_language(text);
#     subprocess.Popen([kNodePath, "talk.js", language, text]).wait()
#     print "--- timing to speech: " + str(rounded_time() - t) + " ---"
#     subprocess.Popen([kSystemPlayer, kTalkFile]).wait()

def play_filler():
    global filler_thread
    def play_filler_sound():
        print "In thread"
        sound = pydub.AudioSegment.from_mp3("fillers/filler.mp3")
        pydub.playback.play(sound)

    filler_thread = threading.Thread(target=play_filler_sound)
    filler_thread.start()

def text_to_speech(text):
    # Instantiates a client
    print text
    t = rounded_time()
    set_language(text);
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.types.SynthesisInput(text=(text or "mumble mumble"))

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.types.VoiceSelectionParams(
        language_code=language,
        name="en-AU-Standard-C",
        ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)

    # Select the type of audio file you want returned
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3,
        pitch=6.0,
        speaking_rate=.9
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

def speech_to_text():
    # Instantiates a client
    client = speech.SpeechClient()

    wav_buffer = record_from_mic()
    # play_filler()
    # Loads the audio into memory
    with wav_buffer as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code='en-US',
        audio_channel_count=CHANNELS)

    # Detects speech in the audio file
    # To be faster - https://cloud.google.com/speech-to-text/docs/basics#streaming-recognition
    response = client.recognize(config, audio)
    if not response.results or not response.results[0].alternatives:
        return "I don't know what you said."
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
    wav_buffer = io.BytesIO()

    wf = wave.open(wav_buffer, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    wav_buffer.seek(0)  #rewind to the start
    return wav_buffer


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
