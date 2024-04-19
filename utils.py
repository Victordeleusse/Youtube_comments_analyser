import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from datetime import datetime, date, timedelta
import requests
import json
from google.cloud import storage

load_dotenv()
api_key = os.getenv("KEY_API")
youtube_owner_name = os.getenv("TF_VAR_NAME")
youtube = build('youtube', 'v3', developerKey=api_key)

# Store pertinent Data from comment
class Message:
    def __init__(self, index, text, authorName, authorID, publishedAt):
        self.index = index
        self.text = text
        self.authorName = authorName
        self.authorID = authorID
        self.publishedAt = publishedAt.split("T")[0]
        
# Retrieve video information
def get_video_info(video_id):
    video_response = youtube.videos().list(part='snippet', id=video_id).execute()
    if video_response['items']:
        video_info = video_response['items'][0]['snippet']
        video_title = video_info['title']
        channel_id = video_info['channelId']
        return video_title, channel_id
    else:
        return None, None

# Retrieve channel information
def get_channel_name(channel_id):
    channel_response = youtube.channels().list(part='snippet', id=channel_id).execute()
    if channel_response['items']:
        return channel_response['items'][0]['snippet']['title']
    else:
        return None

# Load all comments from the video list
def load_comments(bucket_name, video_ids: list, api_key: str):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        videos_messages = {}
        for video in video_ids:
            video_name = get_video_info(video)[0]
            print(f"VIDEO_NAME: {video_name}")
            next_page_token = ''
            messages = []
            count = 0
            while True:
                url = f"https://www.googleapis.com/youtube/v3/commentThreads?key={api_key}&textFormat=plainText&part=snippet&videoId={video}&maxResults=100&pageToken={next_page_token}"
                response = requests.get(url)
                max_index  = -1
                if response.status_code == 200:
                    destination_blob_name = f"{video_name}.json".replace(" ", "_").lower()
                    blob = bucket.blob(destination_blob_name)
                    if blob.exists():
                        existing_data = blob.download_as_text()
                        if existing_data:
                            existing_data_json = json.loads(existing_data) if existing_data else []
                            max_index = len(existing_data_json) - 1
                    data = response.json()
                    for index, item in enumerate(data['items']):
                        snippet = item['snippet']
                        topLevelComment = snippet['topLevelComment']
                        snippet2 = topLevelComment['snippet']
                        messages.append(Message(index + max_index + 1 + count, snippet2['textDisplay'], snippet2['authorDisplayName'], snippet2['authorChannelId']['value'], snippet2['publishedAt']))
                    next_page_token = data.get('nextPageToken')
                    if not next_page_token:
                        break
                    count += 100
                else:
                    break
                videos_messages[video_name] = messages
        return videos_messages
    except Exception as e:
        print(f"An error occurred! {e}")

# First upload to GCS : 
#   - The bucket has been created through Terraform script
#   - Creation of the "video blob"
def first_upload_to_gcs(bucket_name, video_ids: list, api_key: str):
    videos_messages = load_comments(bucket_name, video_ids, api_key)
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    for video_name, messages in videos_messages.items():
        destination_blob_name = f"{video_name}.json".replace(" ", "_").lower()
        blob = bucket.blob(destination_blob_name)
        if blob.exists():
            print(f"Le blob {destination_blob_name} existe déjà, passage à la vidéo suivante.")
        else:
            data_string = json.dumps([message.__dict__ for message in messages], ensure_ascii=False).encode('utf-8')
            blob.upload_from_string(data_string, content_type='application/json')
            print(f"Data uploaded to {destination_blob_name}.")
    
def get_prw_week():
    today = date.today()
    day_list = []
    for i in range(0, 9):
        day = today - timedelta(days=i)
        day_list.append(day.strftime("%Y-%m-%d"))
    print(f"DAY PRW WEEK : {day_list}")
    return day_list

def get_prw_day():
    today = date.today()
    day_list = []
    for i in range(0, 1):
        day = today - timedelta(days=i)
        day_list.append(day.strftime("%Y-%m-%d"))
    # print(f"DAY LIST : {day_list}")
    return day_list

# To select comments from the past week only 
def select_week_comments(videos_messages: dict):
    day_list = get_prw_week()
    prw_week_messages = {}
    for video_name, messages in videos_messages.items():
        prw_week_messages[video_name] = []
        for message in messages:
            if message.publishedAt in day_list:
                prw_week_messages[video_name].append(message)
    return prw_week_messages

# To select comments from the past day only 
def select_day_comments(videos_messages: dict):
    day_list = get_prw_day()
    prw_day_messages = {}
    for video_name, messages in videos_messages.items():
        prw_day_messages[video_name] = []
        for message in messages:
            if message.publishedAt in day_list:
                prw_day_messages[video_name].append(message)
    return prw_day_messages

# if __name__ == "__main__":
#     get_prw_week()