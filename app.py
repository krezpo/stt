#import translate, os, sentiment, synthesize
import speech_recognition as sr
import os
import requests
from flask import Flask, jsonify, request#, render_template, url_for, send_from_directory
from pydub import AudioSegment

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def index():
	return jsonify({"message":"Hello Json!"})

@app.route('/get-file', methods=['POST'])
def get_file():
    data = request.get_json()
    uri  = data['uri']
    r = requests.get(uri, allow_redirects=True)
    #print(r.headers.get('content-type'))

    if r.headers.get('content-type') == "audio/ogg":

        source = "{}{}".format(uri.split("/")[-1], ".ogg")
        open(source, 'wb').write(r.content)

    #print(uri)

    return data


@app.route('/speech-to-text', methods=['POST'])
def text_to_speech():
    data = request.get_json()
    uri  = data['uri']
    
    r = requests.get(uri, allow_redirects=True)

    if r.headers.get('content-type') == "audio/ogg":

        base = uri.split("/")[-1]
        source = "{}{}".format(base, ".ogg")
        open(source, 'wb').write(r.content)

        recognizer = sr.Recognizer()
        wave = "{}{}".format(base, ".wav")
        
        sound = AudioSegment.from_ogg(source)
        sound.export(wave, format="wav")
        os.remove(source)

        with sr.AudioFile(wave) as audio_source:
            audio = recognizer.record(audio_source)
            data["text"] = recognizer.recognize_google(audio, language='pt-BR')
        
        os.remove(wave)

    return data

if __name__ == '__main__':
    app.run(debug=True)