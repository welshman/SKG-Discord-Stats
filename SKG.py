import requests
import time
import os
import datetime
import json # Import the json module

# --- Configuration ---
WEBHOOK = ""

# European Citizens' Initiative (ECI)
EUROPE_API_URL = "https://eci.ec.europa.eu/045/public/api/report/progression"
EUROPE_PETITION_URL = "https://eci.ec.europa.eu/045/public/"
EUROPE_PETITION_TITLE = "Stop Destroying Videogames"
EUROPE_PETITION_AUTHOR_NAME = "European Citizens' Initiative"
EUROPE_PETITION_ICON_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Flag_of_Europe.svg/2560px-Flag_of_Europe.svg.png"
EUROPE_TARGET_SIGNATURES = 1_000_000

# UK Parliament Petition
UK_PETITION_ID = "702074"
UK_PETITION_API_URL = f"https://petition.parliament.uk/petitions/{UK_PETITION_ID}/count.json"
UK_PETITION_URL = f"https://petition.parliament.uk/petitions/{UK_PETITION_ID}"
UK_PETITION_TITLE = "Prohibit publishers irrevocably disabling video games they have already sold"
UK_PETITION_AUTHOR_NAME = "UK Parliament Petitions"
UK_PETITION_ICON_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Flag_of_the_United_Kingdom_%281-2%29.svg/1920px-Flag_of_the_United_Kingdom_%281-2%29.svg.png"
UK_TARGET_SIGNATURES = 100_000 # Considered for debate at 100,000 signatures

# --- Discord Webhook Content Templates ---

# Template for European Citizens' Initiative message
eu_content_template = {
    "content": "",
    "tts": False,
    "embeds": [
        {
            "id": 652627557, # This ID is arbitrary for the embed itself, not the Discord message ID
            "description": "",
            "timestamp": "",
            "color": 13158, # A blue-ish color
            "fields": [],
            "url": EUROPE_PETITION_URL,
            "title": EUROPE_PETITION_TITLE,
            "author": {
                "name": EUROPE_PETITION_AUTHOR_NAME,
                "url": EUROPE_PETITION_URL,
                "icon_url": EUROPE_PETITION_ICON_URL
            },
            "footer": {
                "text": "Checked:"
            }
        }
    ],
    "components": [],
    "actions": {},
    "flags": 0,
    "username": "Stop Killing Games - EU ECI",
    "avatar_url": "https://files.catbox.moe/255del.png"
}

# Template for UK Parliament Petition message
uk_content_template = {
    "content": "",
    "tts": False,
    "embeds": [
        {
            "id": 652627558, # Different ID for this embed
            "description": "",
            "timestamp": "",
            "color": 16711680, # A red-ish color
            "fields": [],
            "url": UK_PETITION_URL,
            "title": UK_PETITION_TITLE,
            "author": {
                "name": UK_PETITION_AUTHOR_NAME,
                "url": UK_PETITION_URL,
                "icon_url": UK_PETITION_ICON_URL
            },
            "footer": {
                "text": "Checked:"
            }
        }
    ],
    "components": [],
    "actions": {},
    "flags": 0,
    "username": "Stop Killing Games - UK Petition",
    "avatar_url": "https://files.catbox.moe/255del.png"
}

# File to store message IDs
MESSAGE_IDS_FILE = "message_ids.json"

# --- Functions to get petition data ---

def get_eu_petition_data():
    """
    Fetches the current signature count for the European Citizens' Initiative.
    Updates the eu_content_template with the latest data and timestamp.
    Returns the updated dictionary.
    """
    try:
        response = requests.get(EUROPE_API_URL, headers={'Cache-Control': 'no-cache'})
        response.raise_for_status() # Raise an exception for HTTP errors
        counts = response.json()["signatureCount"]
        
        current_content = eu_content_template.copy()
        current_content["embeds"][0]["description"] = f"Signatures: {counts:,} / {EUROPE_TARGET_SIGNATURES:,}"
        current_content["embeds"][0]["timestamp"] = datetime.datetime.utcnow().isoformat() + 'Z'
        return current_content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching EU petition data: {e}")
        return None
    except KeyError:
        print("Error: 'signatureCount' not found in EU petition API response.")
        return None

def get_uk_petition_data():
    """
    Fetches the current signature count for the UK Parliament Petition.
    Updates the uk_content_template with the latest data and timestamp.
    Returns the updated dictionary.
    """
    try:
        response = requests.get(UK_PETITION_API_URL, headers={'Cache-Control': 'no-cache'})
        response.raise_for_status() # Raise an exception for HTTP errors
        counts = response.json()["signature_count"]
        
        current_content = uk_content_template.copy()
        current_content["embeds"][0]["description"] = f"Signatures: {counts:,} / {UK_TARGET_SIGNATURES:,}"
        current_content["embeds"][0]["timestamp"] = datetime.datetime.utcnow().isoformat() + 'Z'
        return current_content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching UK petition data: {e}")
        return None
    except KeyError:
        print("Error: 'signature_count' not found in UK petition API response.")
        return None

# --- Message ID Management ---

def load_message_ids():
    """Loads message IDs from a JSON file."""
    if os.path.exists(MESSAGE_IDS_FILE):
        with open(MESSAGE_IDS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_message_ids(ids):
    """Saves message IDs to a JSON file."""
    with open(MESSAGE_IDS_FILE, "w") as f:
        json.dump(ids, f)

# --- Main Logic ---

def main():
    message_ids = load_message_ids()

    # Initialize EU message
    if "eu_message_id" not in message_ids:
        print("Sending initial EU petition message...")
        eu_data = get_eu_petition_data()
        if eu_data:
            try:
                response = requests.post(WEBHOOK + "?wait=true", json=eu_data)
                response.raise_for_status()
                message_ids["eu_message_id"] = response.json()["id"]
                save_message_ids(message_ids)
                print(f"Initial EU message sent with ID: {message_ids['eu_message_id']}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to send initial EU message: {e}")
        else:
            print("Could not get initial EU petition data. Skipping initial message.")

    # Initialize UK message
    if "uk_message_id" not in message_ids:
        print("Sending initial UK petition message...")
        uk_data = get_uk_petition_data()
        if uk_data:
            try:
                response = requests.post(WEBHOOK + "?wait=true", json=uk_data)
                response.raise_for_status()
                message_ids["uk_message_id"] = response.json()["id"]
                save_message_ids(message_ids)
                print(f"Initial UK message sent with ID: {message_ids['uk_message_id']}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to send initial UK message: {e}")
        else:
            print("Could not get initial UK petition data. Skipping initial message.")

    # Main update loop
    while True:
        print("Checking for updates...")
        
        # Update EU petition
        eu_current_data = get_eu_petition_data()
        if eu_current_data and "eu_message_id" in message_ids:
            try:
                print(f"Updating EU message ID: {message_ids['eu_message_id']}")
                response = requests.patch(f"{WEBHOOK}/messages/{message_ids['eu_message_id']}", json=eu_current_data)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Failed to update EU message: {e}")
        elif "eu_message_id" not in message_ids:
            print("EU message ID not found. Skipping EU update.")
        
        # Update UK petition
        uk_current_data = get_uk_petition_data()
        if uk_current_data and "uk_message_id" in message_ids:
            try:
                print(f"Updating UK message ID: {message_ids['uk_message_id']}")
                response = requests.patch(f"{WEBHOOK}/messages/{message_ids['uk_message_id']}", json=uk_current_data)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Failed to update UK message: {e}")
        elif "uk_message_id" not in message_ids:
            print("UK message ID not found. Skipping UK update.")

        print("Waiting for 30 seconds...")
        time.sleep(30)

if __name__ == "__main__":
    main()
