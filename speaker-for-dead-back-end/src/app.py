# app.py (Flask server)
import re
from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS
from src.SpeakerForTheDead import SpeakerForTheDead
from src.MarkBillinghurst import MarkBillinghurst
from src.CustomClone import *
from src.api_key import eleven_labs_api_key
from src.create_video import *
from elevenlabs import generate, stream
import threading
import time
from werkzeug.utils import secure_filename
import requests
import json


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)  # Enable CORS for all routes

#this will be created when first conversing with a custom clone 
CustomCloneInstance = None

#constructor for default Mark Billinghurst Clone
MB = MarkBillinghurst()

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    
    
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    
def emit_message_with_delay():
    time.sleep(3)
    socketio.emit('audio_stream_started', {'message': 'audio_stream_started'})


@app.route('/image_uploads/<path:filename>')
def get_image(filename):
    # Use send_file to send the image file as a response
    return send_from_directory('image_uploads', filename)

@app.route('/custom_clone_videos/<path:filename>')
def get_video(filename):
    # Use send_file to send the image file as a response
    return send_from_directory('custom_clone_videos', filename)

@app.route('/api/get_clone_data', methods=['GET'])
def get_clone_data():
    data = []
    with open('clone_data.json', 'r') as json_file:
        for line in json_file:
            data.append(json.loads(line))
    return jsonify(data)

#this method is called from front end for custom clones
@app.route('/api/custom_clone_chat', methods=['POST'])
def send_and_receive_text_custom_clone():

    data = request.json  #text is sent as JSON data
    received_text = data.get('text', '')
    clone_name = data.get('name')
    custom_voice_id = data.get('customVoiceID')
    print("VOICE " + custom_voice_id)
    
    global CustomCloneInstance  # Declare the variable as global

    # Check if the instance is None (not created yet)
    if CustomCloneInstance is None:
        CustomCloneInstance = create_new_character(clone_name)
   
    # get response from OpenAI/vector DB
    response_text = CustomCloneInstance.converse_with_word_chunks_generator(received_text)
    
    #interact with elevenlabs api
    audio = generate(
        text=response_text,
        voice=custom_voice_id,
        #model="eleven_monolingual_v1",
        api_key = eleven_labs_api_key,
        stream=True
    )
    
    #look into multi-threading here
    # Create a thread to emit the message with a 5-second delay
    emit_thread = threading.Thread(target=emit_message_with_delay)
    emit_thread.start()
    
    stream(audio) #stream returned audio file from elevenlabs
    
    #this is returned to front end 
    #BUG: cannot return generator object
    response_data = {
        'response_text': response_text
        }
    
    return jsonify("response")

#this method is called from front end for low latency audio clone
@app.route('/api/data', methods=['POST'])
def send_and_receive_text():

    data = request.json  #text is sent as JSON data
    received_text = data.get('text', '')
   
    # get response from OpenAI/vector DB
    response_text = MB.converse_with_word_chunks_generator(received_text)
    
    #interact with elevenlabs api
    audio = generate(
        text=response_text,
        voice="BFVlc4YAgdu8QqOkNgyL",
        #model="eleven_monolingual_v1",
        api_key = eleven_labs_api_key,
        stream=True
    )
    
    #look into multi-threading here
    # Create a thread to emit the message with a 5-second delay
    emit_thread = threading.Thread(target=emit_message_with_delay)
    emit_thread.start()
    
    stream(audio) #stream returned audio file from elevenlabs
    
    #this is returned to front end 
    #BUG: cannot return generator object
    response_data = {
        'response_text': response_text
        }
    
    return jsonify("response")

#this method is called from front end for video based clone
@app.route('/api/data_video', methods=['POST'])
def send_and_receive_text_video():
    data = request.json  #text is sent as JSON data
    received_text = data.get('text', '')
    response_text = MB.converse(received_text)
    
    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/BFVlc4YAgdu8QqOkNgyL"

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

#this method is called from front end to train a custom clone
@app.route('/api/train_clone', methods=['POST'])
def train_clone():
    uploaded_audio_file = request.files['audioFile']
    uploaded_image_file = request.files['imageFile']
    uploaded_context_file = request.files['contextFile']

    if uploaded_audio_file and uploaded_image_file and uploaded_context_file:
        # Ensure the filename is safe and secure
        audio_filename = secure_filename(uploaded_audio_file.filename)
        image_filename = secure_filename(uploaded_image_file.filename)
        voice_name = request.form['name']
        context_filename = secure_filename(voice_name + '.txt')
        
        # Save the uploaded files to a specific directory
        uploaded_audio_file.save(f'audio_uploads/{audio_filename}')
        uploaded_image_file.save(f'image_uploads/{image_filename}')
        uploaded_context_file.save(f'clone_info_uploads/{context_filename}')
        
        #create vector db embeddings for custom clone
        create_new_character(voice_name)
        
        #communicate with eleven labs api to train custom voice

        url = "https://api.elevenlabs.io/v1/voices/add"

        headers = {
          "Accept": "application/json",
          "xi-api-key": eleven_labs_api_key
        }
        
        data = {
            'name': voice_name
    
        }
        
        files = [
            ('files', (f'{audio_filename}', open(f'audio_uploads/{audio_filename}', 'rb'), 'audio/mpeg'))
        ]

        response = requests.post(url, headers=headers, data=data, files=files)
        print(response.text)
        response_data = json.loads(response.text)
        voice_id = response_data.get('voice_id', '')
        
        #emit message to front end that voice was trained
        socketio.emit('voice_trained_successfully', {'message': 'voice_trained_successfully'})

        #communicate with replicate api to create idle and talking videos
        idle_path, talking_path = generate_videos_for_custom_clones(f'image_uploads/{image_filename}', voice_name)
        
        #emit message to front end that voice was trained
        socketio.emit('videos_trained_successfully', {'message': 'videos_trained_successfully'})
        
        # Create a dictionary with the values you want to write to the JSON file
        result_data = {
            'clone_name': voice_name,
            'voice_id': voice_id,
            'idle_path': idle_path,
            'talking_path': talking_path,
            'image_path': f'image_uploads/{image_filename}'
        }

        # Append the dictionary as a new line in the JSON file
        with open('clone_data.json', 'a') as json_file:
            json.dump(result_data, json_file)
            json_file.write('\n')  # Add a newline character to separate entries

        return jsonify({'message': 'Clone trained successfully'})

    return jsonify({'message': 'No file uploaded'})

    

if __name__ == '__main__':
    #app.run()
    socketio.run(app, allow_unsafe_werkzeug=True)
    #socketio.run(app)
    
    
    
    
    
    
    
    