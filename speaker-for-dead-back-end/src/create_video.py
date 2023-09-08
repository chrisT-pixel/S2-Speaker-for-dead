from src.api_key import eleven_labs_api_key
import requests
import replicate
from os import path
from pydub import AudioSegment
import math


def get_most_recent_audio_as_mpeg():

    # GET MOST RECENT AUDIO ID FROM ELEVENLABS
    PAGE_SIZE = 1
    url = "https://api.elevenlabs.io/v1/history"
    
    headers = {
      "Accept": "application/json",
      "xi-api-key": eleven_labs_api_key
    }
    
    history = []
    last_history_item_id = None
    
    params = {
      "page_size": PAGE_SIZE,
      "start_after_history_item_id": last_history_item_id
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    history.extend(data["history"])
    last_history_item_id = data["last_history_item_id"]
    
    url = "https://api.elevenlabs.io/v1/history/download"
    
    headers = {
      "Accept": "*/*",
      "Content-Type": "application/json",
      "xi-api-key": eleven_labs_api_key
    }
    
    data = {
      "history_item_ids": [
        last_history_item_id
      ]
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        content_type = response.headers.get("Content-Type")
        if content_type == "audio/mpeg":
            mpeg_filename = "current-response.mpeg"  # Choose a filename for the downloaded MP3 file
            with open(mpeg_filename, "wb") as f:
                f.write(response.content)
            print(f"audio file downloaded and saved as '{mpeg_filename}'")
        else:
            print("Response content is not an audio file.")
    else:
        print(f"Request failed with status code: {response.status_code}")
    
#END GET RECENT MP3 FROM ELEVENLABS

def convert_mpeg_to_wav(input):
    sound = AudioSegment.from_mp3(input)
    sound.export("current-response.wav", format="wav")
    print("converted mpeg to a wav - ready for machine learning")

def generate_talking_response_make_it_talk():
    output = replicate.run(
        "cudanexus/makeittalk:e63aa3e0830945d12340aba53c63e27288b5705eec0c8ea0db5b144c5d64dbf6",
        input={ "image": open("mark-billinghurst.jpg", "rb"),
                "audio": open("current-response.wav", "rb") 
                }
    )
    print(output)

def generate_talking_response_sad_face():
    output = replicate.run(
        "cjwbw/sadtalker:3aa3dac9353cc4d6bd62a8f95957bd844003b401ca4e4a9b33baa574c549d376",
        input={"source_image": open("mark-billinghurst.jpg", "rb"),
               "driven_audio": open("current-response.wav", "rb") 
               }
    )
    print(output)
    return output

def chop_audio_into_chunks():

    # Input MP3 file path
    input_file = "mark-speaking-long.mp3"
    
    # Load the MP3 file
    audio = AudioSegment.from_mp3(input_file)
    
    # Duration of each chunk in milliseconds (60 seconds)
    chunk_duration = 60 * 1000
    
    # Calculate the total number of chunks needed
    total_chunks = math.ceil(len(audio) / chunk_duration)
    
    # Output directory for the chunks
    output_directory = "audio_chunks/"
    
    # Iterate through the chunks
    for i in range(total_chunks):
        start_time = i * chunk_duration
        end_time = (i + 1) * chunk_duration
    
        # Extract the chunk
        chunk = audio[start_time:end_time]
    
        # Save the chunk to an output file
        output_file = f"{output_directory}chunk_{i+1}.mp3"
        chunk.export(output_file, format="mp3")
    
    print("MP3 file chopped into one-minute chunks.")
    
url = "https://api.elevenlabs.io/v1/voices"

def printAvailableVoiceDetails():

    headers = {
      "Accept": "application/json",
      "xi-api-key": eleven_labs_api_key
    }
    
    response = requests.get(url, headers=headers)
    
    print(response.text)








