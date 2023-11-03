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

output_chunks_length = 0  # Initialize the variable

@socketio.on('output_chunks_length')
def handle_output_chunks_length(length):
    global output_chunks_length  # Declare the variable as global
    output_chunks_length = length  # Store the received value in the variable
    print(f'Received output_chunks_length: {length}')


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
    
def emit_message_with_short_delay(): #used for short responses
    time.sleep(1.2)
    socketio.emit('audio_stream_started', {'message': 'audio_stream_started'})
    
def emit_message_with_medium_delay(): #used for medium responses
    time.sleep(1.6)
    socketio.emit('audio_stream_started', {'message': 'audio_stream_started'})
    
def emit_message_with_long_delay(): #used for long responses
    time.sleep(2)
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
            print(line)
    return jsonify(data)

#this method is called from front end to converse with custom clones
@app.route('/api/custom_clone_chat', methods=['POST'])
def send_and_receive_text_custom_clone():

    data = request.json  #data is sent as JSON 
    received_text = data.get('text', '')
    clone_name = data.get('name')
    custom_voice_id = data.get('customVoiceID')
    
    global CustomCloneInstance  # Declare the variable as global
    CustomCloneInstance = create_new_character(clone_name)
    
    # get response from OpenAI/vector DB
    #response_text = CustomCloneInstance.converse_with_word_chunks_generator(received_text)
    response_text = CustomCloneInstance.converse_davinci_legacy(received_text)
    
    response_length = len(response_text)

    #interact with elevenlabs api
    audio = generate(
        text=response_text,
        voice=custom_voice_id,
        model="eleven_monolingual_v1",
        api_key = eleven_labs_api_key,
        stream=True
    )
    
    #multi thread to not intefere with main thread fetching audio from elevenlabs
    if(response_length < 50):
        emit_thread = threading.Thread(target=emit_message_with_short_delay)
        print("short response")
        emit_thread.start()
        
    elif(response_length < 100):
        emit_thread = threading.Thread(target=emit_message_with_medium_delay)
        print("medium response")
        emit_thread.start()
    
    else:
        emit_thread = threading.Thread(target=emit_message_with_long_delay)
        print("long response")
        emit_thread.start()
        

    stream(audio) #stream returned audio file from elevenlabs
    
    #this is returned to front end 
    response_data = {
        'response_text': response_text
        }
    
    return jsonify(response_data)

#this method is called from front end to converse with Mark B low latency audio clone
@app.route('/api/data', methods=['POST'])
def send_and_receive_text():

    data = request.json  #text is sent as JSON data
    received_text = data.get('text', '')
   
    # get response from OpenAI/vector DB
    #response_text = MB.converse_with_word_chunks_generator(received_text)
    response_text = MB.converse_davinci_legacy(received_text)
    
    response_length = len(response_text)
    
    #interact with elevenlabs api
    audio = generate(
        text=response_text,
        voice="BFVlc4YAgdu8QqOkNgyL",
        model="eleven_monolingual_v1",
        api_key = eleven_labs_api_key,
        stream=True
    )
    
    #multi thread to not intefere with main thread fetching audio from elevenlabs
    if(response_length < 50):
        emit_thread = threading.Thread(target=emit_message_with_short_delay)
        print("short response")
        emit_thread.start()
        
    elif(response_length < 100):
        emit_thread = threading.Thread(target=emit_message_with_medium_delay)
        print("medium response")
        emit_thread.start()
    
    else:
        emit_thread = threading.Thread(target=emit_message_with_long_delay)
        print("long response")
        emit_thread.start()
    
    stream(audio) #stream returned audio file from elevenlabs
    
    #this is returned to front end 
    response_data = {
        'response_text': response_text
        }
    
    return jsonify(response_data)

#this method is called from front end to converse with Mark B video based clone
@app.route('/api/data_video', methods=['POST'])
def send_and_receive_text_video():
    data = request.json  #text is sent as JSON data
    received_text = data.get('text', '')
    response_text = MB.converse_davinci_legacy(received_text)
    
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
                
    convert_mpeg_to_wav("output-new.mp3") #Marks current audio output
    response_video = generate_talking_response_sad_face()
    
    response_data = {
        'response_text': response_text,
        'response_video': response_video
        }
    
    return jsonify("response")

#this method is called from front end to train a custom clone using pre-prepared materials
@app.route('/api/train_clone_uploads_only', methods=['POST'])
def train_clone_uploads_only():
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

#this method is called from front end to train a custom clone with a pretrained voice
@app.route('/api/train_clone_uploads_and_pre_trained_voice', methods=['POST'])
def train_clone_uploads_and_pre_trained_voice():
   
    uploaded_image_file = request.files['imageFile']
    uploaded_context_file = request.files['contextFile']

    if uploaded_image_file and uploaded_context_file:
        
        # Ensure the filename is safe and secure
        image_filename = secure_filename(uploaded_image_file.filename)
        voice_name = request.form['name']
        voice_id = request.form['voiceID']
        context_filename = secure_filename(voice_name + '.txt')

        # Save the uploaded files to a specific directory
        uploaded_image_file.save(f'image_uploads/{image_filename}')
        uploaded_context_file.save(f'clone_info_uploads/{context_filename}')

        #create vector db embeddings for custom clone
        create_new_character(voice_name)

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

#this method is called from front end to train a custom clone using in-app materials
@app.route('/api/train_clone', methods=['POST'])
def train_clone():
    
    uploaded_audio_file = request.files['audioBlob']
    uploaded_image_file = request.files['imageBlob']
    uploaded_context_file = request.files['contextFile']

    if uploaded_audio_file and uploaded_image_file and uploaded_context_file:
        # Ensure the filename is safe and secure
        audio_filename = secure_filename(uploaded_audio_file.filename)
        image_filename = secure_filename(uploaded_image_file.filename)
        voice_name = request.form['name']
        
        context_content = uploaded_context_file.read()  # Read the content of the context file as text
        # Define the file path and name for the context text file.
        context_file_path = 'clone_info_uploads/'  # Modify this with the actual path.
        context_filename = secure_filename(voice_name + '.txt')
            
        # Save the context content to a text file.
        with open(f'{context_file_path}/{context_filename}', 'w') as file:
            file.write(context_content.decode('utf-8'))  # Decode the bytes to a string before writing
        
        # Save the uploaded image with the secure filename
        img_file_path = f'image_uploads/{image_filename}'
        uploaded_image_file.save(img_file_path)
        
        cropUploadedImage(img_file_path)
            
        # Save the other uploaded files to a specific directory
        uploaded_audio_file.save(f'audio_uploads/{audio_filename}')
        #uploaded_context_file.save(f'clone_info_uploads/{context_filename}')
        
        
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
            #'date_created': date_created
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
    
    
    
    
    
    
    
    