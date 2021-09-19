import speech_recognition as sr
import os
import requests
from flask import Flask, jsonify, request
from flask_api import status
from pydub import AudioSegment

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


def is_downloadable(url):

    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')

    if content_type == None:
        return False

    if content_type.lower() in ['text', 'html']:
        return False

    return True


@app.route('/')
def index():
    return jsonify({"message": "Hello World!"})


@app.route('/speech-to-text', methods=['POST'])
def text_to_speech():
    data = request.get_json()

    if 'language' not in data or 'uri' not in data:
        return "", status.HTTP_400_BAD_REQUEST

    uri = data['uri']
    language = data['language']

    try:
        if not is_downloadable(uri):
            return "", status.HTTP_400_BAD_REQUEST
    except Exception as e:
        return jsonify({"error": e}), status.HTTP_503_SERVICE_UNAVAILABLE

    try:
        r = requests.get(uri, allow_redirects=True)
    except Exception as e:
        return jsonify({"error": e}), status.HTTP_503_SERVICE_UNAVAILABLE

    if r.headers.get('content-type') != "audio/ogg":
        return "", status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

    try:
        base_filename = uri.split("/")[-1]
        source_file = "{}{}".format(base_filename, ".ogg")
        open(source_file, 'wb').write(r.content)

        recognizer = sr.Recognizer()
        destination_file = "{}{}".format(base_filename, ".wav")

        sound = AudioSegment.from_ogg(source_file)
        sound.export(destination_file, format="wav")
        os.remove(source_file)

        with sr.AudioFile(destination_file) as audio_source:
            audio = recognizer.record(audio_source)
            data["text"] = recognizer.recognize_google(
                audio, language=language)

        os.remove(destination_file)

        return data, status.HTTP_200_OK

    except Exception as e:
        return jsonify({"error": e}), status.HTTP_500_INTERNAL_SERVER_ERROR


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")
