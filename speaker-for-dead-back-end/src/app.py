# app.py (Flask server)
import re
from flask import Flask, jsonify, request
from flask_cors import CORS
from src.SpeakerForTheDead import SpeakerForTheDead
from src.MarkBillinghurst import MarkBillinghurst
from src.api_key import eleven_labs_api_key
from elevenlabs import generate, stream

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

MB = MarkBillinghurst()

#only needed if using converse() and NOT converse_with_word_chunks_generator()
def break_string_into_chunks(input_string, chunk_size=4):
    words = re.findall(r'\w+', input_string)
    chunks = [words[i:i+chunk_size] for i in range(0, len(words), chunk_size)]
    return [' '.join(chunk) + ' ' for chunk in chunks]

#only needed if using converse() and NOT converse_with_word_chunks_generator()
def text_input_stream(chunks_of_text):
    for i, chunk in enumerate(chunks_of_text, start=1):
        yield chunk

@app.route('/api/data', methods=['POST'])
def send_and_receive_text():
    
    data = request.json  #text is sent as JSON data
    received_text = data.get('text', '')
   
    # get response from OpenAI/vector DB
    #response_text = MB.converse(received_text)
    response_text = MB.converse_with_word_chunks_generator(received_text)
    #returns "user then whatever the question was, not the answer
    
    #this is eventually returned to front end
    response_data = {'response_text': response_text}
    
    #break response up into chunks of 4 words
    #chunks = break_string_into_chunks(response_text)
    
    #interact with elevenlabs api
    audio = generate(
        text=response_text,
        #text=text_input_stream(chunks),
        voice="Bella",
        model="eleven_monolingual_v1",
        api_key = eleven_labs_api_key,
        stream=True
        
    )
    
    
    stream(audio) #stream returned audio file from elevenlabs
    
    return jsonify(response_data)

    
    

if __name__ == '__main__':
    app.run()