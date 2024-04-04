import os
from dotenv import load_dotenv
from utils import *
# import argparse
from update_comments import update_comments

load_dotenv()
api_key = os.getenv("KEY_API")
video_ids = [os.getenv("VIDEO_ID_1"), os.getenv("VIDEO_ID_2")]
youtube_owner_name = os.getenv("TF_VAR_NAME")

# def parse_arguments():
#     parser = argparse.ArgumentParser(description="Youtube comments analyzer")
#     parser.add_argument("--videos", required=True, nargs='+', help="Video(s) comment(s) to be analyzed. Please enter python3 get_comments.py --videos XXX YYY ZZZ")
#     return parser.parse_args()

if __name__ == "__main__":
    # args = parse_arguments()
    # video_ids = args.videos
    first_upload_to_gcs(youtube_owner_name, video_ids, api_key)
    update_comments(video_ids, api_key)
    # for name, messages_lst in videos_messages.items():
    #     for message in messages_lst:
    #         print(message.publishedAt)
    
    # print("\n\n =============================== \n\n")
    # last_day_messages = update_comments(video_ids, api_key)
    # for name, messages_lst in last_day_messages.items():
    #     for message in messages_lst:
    #         print(message.authorName)
    #         print(message.publishedAt)
    