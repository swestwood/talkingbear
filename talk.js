/**
 * Calls the Google Text to Speech API and saves the output as an mp3.
 *
 * Usage: node talk.js "some string"
 * Outputs: talk.mp3 file with text-to-voice version of the string
 *
 * Relies on GOOGLE_APPLICATION_CREDENTIALS env var being properly set up.
 *
 * Reference: https://cloud.google.com/text-to-speech/docs/create-audio
 */

const fs = require('fs');
const kTalkFile = "generated_talk.mp3";

// Google Cloud client library
const textToSpeech = require('@google-cloud/text-to-speech');

const client = new textToSpeech.TextToSpeechClient();

// The text to synthesize, passed from the command line
var args = process.argv.slice(2);
const text = args.length > 0 ? args[0] : 'Hello, world!';

console.log("Converting: " + text)

const request = {
    input: {text: text},
    voice: {
        languageCode: 'en-AU',
        ssmlGender: 'FEMALE',
        name: "en-AU-Standard-C",
    },
    audioConfig: {
        audioEncoding: 'MP3',
        "pitch": "6.0",
        speakingRate: .9
    }
};

client.synthesizeSpeech(request, (err, response) => {
    if (err) {
        console.error('Error:', err);
        return;
    }

    // Write the binary audio content to a local file
    // File name is used in speech_echo.py as well
    fs.writeFile(kTalkFile, response.audioContent, "binary", err => {
        if (err) {
            console.error('Error:', err);
            return;
        }
        console.log("Audio content written to file: " + kTalkFile);
    });
});

