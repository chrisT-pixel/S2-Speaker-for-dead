from src.api_key import eleven_labs_api_key
import requests
import replicate
from os import path
from pydub import AudioSegment
import math
from PIL import Image
#import pixellib
#from tensorflow.keras.layers import BatchNormalization
#from pixellib.tune_bg import alter_bg


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


def generate_videos_for_custom_clones(path_to_file, name):
    
    outputIdle = replicate.run(
    
        "wyhsirius/lia:4ce4e4aff5bd28c6958b1e3e7628ea80718be56672d92ea8039039a3a152e67d",
    input={"img_source": open(path_to_file, "rb"),
           "driving_video": open("training_videos/idle.mp4", "rb")
           }
    )
    
    print(outputIdle)
    
    outputTalking = replicate.run(
    
        "wyhsirius/lia:4ce4e4aff5bd28c6958b1e3e7628ea80718be56672d92ea8039039a3a152e67d",
    input={"img_source": open(path_to_file, "rb"),
           "driving_video": open("training_videos/talking.mov", "rb")
           }
    )
    
    print(outputTalking)
    
    local_idle_path = f"custom_clone_videos/{name}_idle.mp4"
    local_talking_path = f"custom_clone_videos/{name}_talking.mp4"
    
    downloadVideoFromReplicate(outputIdle, local_idle_path)
    downloadVideoFromReplicate(outputTalking, local_talking_path)
    
    return local_idle_path, local_talking_path
    

def downloadVideoFromReplicate(video_url, local_file_path):
    try:
        # Send an HTTP GET request to the video URL
        response = requests.get(video_url, stream=True)
    
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Open a local file for binary write
            with open(local_file_path, "wb") as file:
                # Iterate through the content in chunks and write to the file
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
    
            print(f"Video downloaded and saved to {local_file_path}")
        else:
            print(f"Failed to download video. Status code: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    
    


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
    
def cropUploadedImage(file_name):
    # Open the image
    image = Image.open(file_name)

    # Define the cropping rectangle (left, upper, right, lower)
    left = 280
    upper = 0  # No cropping from the top
    right = image.width - 280
    lower = image.height  # No cropping from the bottom

    # Crop the image
    cropped_image = image.crop((left, upper, right, lower))

    # Save the cropped image
    cropped_image.save(file_name)
    
'''def blurImageBackground():
    change_bg = alter_bg()
    img_file_path = f'image_uploads/Clay-face.jpg'
    change_bg.load_pascalvoc_model("deeplabv3_xception_tf_dim_ordering_tf_kernels.h5")
    change_bg.color_bg(img_file_path, colors = (0,128,0), output_image_name="colored_bg.jpg")
    '''
#blurImageBackground()

    








