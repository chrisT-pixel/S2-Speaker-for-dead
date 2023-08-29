# app.py (Flask server)
import re
from flask import Flask, jsonify, request
from flask_cors import CORS
from src.SpeakerForTheDead import SpeakerForTheDead
from src.MarkBillinghurst import MarkBillinghurst
from src.api_key import eleven_labs_api_key
from src.create_video import *
from elevenlabs import generate, stream

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


MB = MarkBillinghurst()

#@app.route('/api/data', methods=['POST'])
'''def send_and_receive_text():
    
    data = request.json  #text is sent as JSON data
    received_text = data.get('text', '')
   
    # get response from OpenAI/vector DB
    response_text = MB.converse_with_word_chunks_generator(received_text)
    
    #interact with elevenlabs api
    audio = generate(
        text=response_text,
        voice="Bella",
        model="eleven_monolingual_v1",
        api_key = eleven_labs_api_key,
        stream=True
    )
    
    stream(audio) #stream returned audio file from elevenlabs
    
    #this is returned to front end 
    #BUG: cannot return generator object
    response_data = {
        'response_text': response_text
        }
    
    return jsonify(response_data)'''

@app.route('/api/data', methods=['POST'])
def send_and_receive_text():
    data = request.json  #text is sent as JSON data
    received_text = data.get('text', '')
    response_text = MB.converse(received_text)
    
    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/2EiwWnXFnvU5JabPnv8n"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": eleven_labs_api_key
        }

    data = {
        "text": response_text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
            }
        }

    response = requests.post(url, json=data, headers=headers)
    with open('output-new.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
                
    
    
    convert_mpeg_to_wav("output-new.mp3")
    response_video = generate_talking_response_sad_face()
    
    response_data = {
        'response_text': response_text,
        'response_video': response_video
        }
    
    return jsonify(response_data)

    
    

if __name__ == '__main__':
    app.run()