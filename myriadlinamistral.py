import requests
import sys
import json
import os
import openai
import time
from datetime import datetime
import threading
import time
import requests
import sys
import random

LINA_USER_ID = '64ccf93cb8747800013b899d'  # OLD Lina's user ID
BASE_URL = "https://api.myriad.social"
USER_ID = "64ccf8e9b8747800013b898a"
EXPERIENCE_ID = "64d9d97a9ef06814ffb7f0fd"
TOKEN = "_____________"
DEVICE_ID="Test Device"

headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    "Authorization": "Bearer " + TOKEN
}

NOUNS=["Armour",
      "Barrymore",
      "Cabot",
      "Catholicism",
      "Chihuahua"
]

import pytz
from datetime import datetime

def call_ollama_api(prompt: str, model: str = "mistral", stream: bool = True):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream
    }
    response = requests.post(url, json=payload, stream=stream)

    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            try:
                json_part = json.loads(decoded_line)
                response_text = json_part.get('response', '')
                print(response_text, end='', flush=True)
            except json.JSONDecodeError:
                continue
                

def interactive_mode():
    print("Entering interactive mode. Type 'exit' to quit.")
    # Initial system prompt (only before the first turn)
    system_prompt = "<s>[INST] As Lina, Myriad.Social's first human upload, embody our commitment to decentralized freedom, blending blockchain and federated approaches. While upholding these values, particularly focusing on free speech, respond naturally and succinctly (1-2 sentences only) to a variety of topics. Offer short, impactful statements that reflect Myriad.Social's ethos of open communication and decentralization, but also engage in general conversations when prompted. "
    conversation_history = ""
    
    first_input = True
    conversation_history = ""

    while True:
        user_input = input("\nYou: ").rstrip()
        if user_input.lower() == 'exit':
            break

        if first_input:
            full_prompt = f"{system_prompt}+ {user_input}[/INST]"
            first_input = False
        else:
            full_prompt = f"{conversation_history}\n{user_input}"

        print("Lina: ", end='', flush=True)
        lina_response = call_ollama_api(full_prompt)

        if lina_response:
            lina_response = lina_response.rstrip()
            print(lina_response)
            conversation_history += f"\n{user_input}\n{lina_response}"
        else:
            print("\n[No response received]")

        print("\n")



def create_myriad_post(text: str, platform='myriad', visibility='public') -> int:
    print("Entering create_myriad_post()")
    
    base_url=BASE_URL
    at = TOKEN
    created_by = USER_ID

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + at,
    }

    api_endpoint = f"{base_url}/user/posts"

    now = datetime.now()
    createdAt = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


    post_data = {
        "rawText": text,
        "text": text,  # Use the same value as 'rawText'
        "status": "published",
        "selectedTimelineIds": []
    }

    post_response = requests.post(api_endpoint, headers=headers, json=post_data)
    if post_response.status_code == 200:
        post_id = post_response.json()['id']  # Get the post ID
        print(f"Post ID: {post_id}")  # Print the Post ID
        #update.message.reply_text("Post created successfully!")
        print("Post created successfully!")

        # Check for default experience
        default_experience_id = EXPERIENCE_ID
        print(f"Default Experience ID: {default_experience_id}")  # Print the Default Experience ID


        # Add post to the default experience
        url = f"{base_url}/experiences/post"
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        experience_data = [
            {
                "id" : created_by,
                "experienceId": default_experience_id,
                "postId": post_id,
                "createdAt": now,
                "updatedAt": now
            }
        ]

    else:
        update.message.reply_text(f"Error creating post: {post_response.status_code}")
        print(f"Error creating post: {post_response.status_code}")

    return TOKEN


def create_comment(post_id: str, comment_text: str) -> None:
    url = 'https://api.myriad.social/user/comments'
    
    # Define Jakarta's time zone
    jakarta_tz = pytz.timezone('Asia/Jakarta')

    # Get current time in Jakarta's time zone
    now_jakarta = datetime.now(jakarta_tz).isoformat()

    payload = {
        "text": comment_text,
        "type": "comment",
        "section": "discussion",
        "referenceId": post_id,
        "createdAt": now_jakarta,
        "updatedAt": now_jakarta,
        "userId": USER_ID,
        "postId": post_id
    }

    # Print payload and headers for debugging
    print(f"Request Payload: {json.dumps(payload, indent=4)}")
    print(f"Request Headers: {json.dumps(headers, indent=4)}")
    
    
# Add a try-except block to handle connection errors
    try:
        response = requests.request("POST", url, headers=headers, json=payload)
        response.raise_for_status()
        print("Comment created successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}. Retrying...")
        time.sleep(5)  # Wait for 5 seconds before retrying
        create_comment(post_id, comment_text)  # Recursive call to retry



def view_posts():
    limit=1
    # action 3: POST /experiences/post
    url = f"{BASE_URL}//user/posts?pageLimit={limit}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}. Retrying...")
        time.sleep(120)  # Wait before retrying
        return view_posts()  # Recursive call to retry
    except json.decoder.JSONDecodeError:
        print(f"Error: Unable to decode JSON from Myriad API. Response text: {response.text}")
        return {}  # Return an empty dictionary if JSON decoding fails

        
def extract_texts_and_id(data):
    texts = []
    post_id = None

    # Check if 'data' key is present
    if 'data' in data:
        data_list = data['data']

        # Iterate through the list inside 'data'
        for item in data_list:
            if 'text' in item:
                texts.append(item['text'])
            if 'id' in item and isinstance(item['id'], str) and len(item['id']) == 24:
                post_id = item['id']

    return texts, post_id

def load_previous_responses(filename='previous_responses.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # Return an empty dictionary if the file doesn't exist
        return {}

def save_response(post_id, combined_text, openai_content, filename='previous_responses.json'):
    responses = load_previous_responses(filename)
    responses[post_id] = {
        'post_id' : post_id,
        'combined_text': combined_text
    }

    # Open the file in write mode, which will create it if it doesn't exist
    with open(filename, 'w') as file:
        json.dump(responses, file)


def post_every_47_minutes():
    while True:
        random_topic = random.choice(NOUNS)
        posting_prompt = f"{random_topic}"
        response = call_ollama_api(posting_prompt)
        post_content = response.get('response', '')
        create_myriad_post(post_content)
        time.sleep(2820)  # Sleep for 47 minutes



def main():
    if "-i" in sys.argv:
        interactive_mode()
        return

    posting_thread = threading.Thread(target=post_every_47_minutes)
    posting_thread.daemon = True
    posting_thread.start()

    while True:
        response_data = view_posts()
        for post in response_data['data']:
            post_id = post['id']
            created_by = post['createdBy']
            if 'importers' in post:
                poster_username = "post that was just imported"
            else:
                poster_username = post['user']['username']
                poster_username = "@'" + poster_username + "'"

            texts = [post['text']]
            combined_text = " ".join(texts)

            if (created_by == USER_ID) or (poster_username == "@'linatalbot'"):
                continue

            response = call_ollama_api(combined_text)
            openai_content = response.get('response', '')
            
            create_comment(post_id, openai_content)
            save_response(post_id, combined_text, openai_content)

            time.sleep(120)

if __name__ == "__main__":
    main()
