import os
import argparse
from dotenv import load_dotenv

from utils import *
from update_comments import update_comments

load_dotenv()
api_key = os.getenv("KEY_API")
video_ids = [os.getenv("VIDEO_ID_1"), os.getenv("VIDEO_ID_2")]
youtube_owner_name = os.getenv("TF_VAR_NAME")

def first_extract_comments_from(video_ids: list, api_key: str):
    try:
        videos_messages = load_comments(video_ids, api_key)
        return videos_messages
    except Exception as e:
        print(f"An error occurred! {e}")

# def parse_arguments():
#     parser = argparse.ArgumentParser(description="Youtube comments analyzer")
#     parser.add_argument("--videos", required=True, nargs='+', help="Video(s) comment(s) to be analyzed. Please enter python3 get_comments.py --videos XXX YYY ZZZ")
#     return parser.parse_args()

if __name__ == "__main__":
    # args = parse_arguments()
    # video_ids = args.videos
    videos_messages = first_extract_comments_from(video_ids, api_key)
    # upload_to_gcs(youtube_owner_name, videos_messages)
    for name, messages_lst in videos_messages.items():
        for message in messages_lst:
            print(message.publishedAt)
    
    print("\n\n =============================== \n\n")
    last_day_messages = update_comments(video_ids, api_key)
    for name, messages_lst in last_day_messages.items():
        for message in messages_lst:
            print(message.publishedAt)
    
    
