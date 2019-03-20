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
const util = require('util');
const kTalkFile = "generated_talk.mp3";
const projectId = 'talkingbear';

// Google Cloud client library

// The text to synthesize, passed from the command line
var args = process.argv.slice(2);
const language = args.length > 0 ? args[0] : "en";
const voicetype = args.length > 1 ? args[1] : 1;
const text = args.length > 2 ? args[2] : 'Hello, world!';

console.log("voicetype: "+voicetype);


var lang = 'en-AU';
var voice = 'en-AU-Standard-C'

if (voicetype == 1) {
    language_code = 'en-AU';
    gender = 'FEMALE';
    language_name = "en-AU-Standard-C";
    speaking_pitch = 6.0;
    speaking_rate = 0.9;
} else if (voicetype == 2) {
    language_code = 'en-GB';
    gender = 'FEMALE';
    language_name = "en-GB-Standard-A";
    speaking_pitch = 6.4;
    speaking_rate = 0.7;
} else if (voicetype == 3) {
    language_code = 'de-DE';
    gender = 'FEMALE';
    language_name = "de-DE-Standard-A";
    speaking_pitch = 2.40;
    speaking_rate = 0.9;
} else if (voicetype == 4) {
    language_code = 'ja-JP';
    gender = 'FEMALE';
    language_name = "ja-JP-Standard-A";
    speaking_pitch = 2.40;
    speaking_rate = 1.23;
}

console.log("Converting phrase: "+text+", in language: "+language);
translate(text, language);


async function translate(text, language) {
    if (language == "en") {
        await convertToSpeech(text);
        return;
    }

    const {Translate} = require('@google-cloud/translate');
    const translationClient = new Translate({projectId});

    console.log("Translating: " + text)
    const [translation] = await translationClient.translate(text, language);
    console.log("Translated text: "+ translation);
    await convertToSpeech(translation);
}

async function convertToSpeech(text) {
    const textToSpeech = require('@google-cloud/text-to-speech');
    const voiceClient = new textToSpeech.TextToSpeechClient();

    const request = {
        input: {text: text},
        voice: {
            languageCode: language_code, // normally 'en-AU'
            ssmlGender: gender, // normally 'FEMALE'
            name: language_name // normally "en-AU-Standard-C"
        },
        audioConfig: {
            audioEncoding: 'MP3',
            pitch: speaking_pitch, // normally 6.0
            speakingRate: speaking_rate // normally .9
        }
    };

    console.log("Converting to voice: " + text)
    const [response] = await voiceClient.synthesizeSpeech(request);
    // Write the binary audio content to a local file
    // File name is used in speech_echo.py as well
    const writeFile = util.promisify(fs.writeFile);
    await writeFile(kTalkFile, response.audioContent, 'binary');
    console.log("Audio content written to file: " + kTalkFile);
}




