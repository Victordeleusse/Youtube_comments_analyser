from dotenv import load_dotenv
load_dotenv()

import os
# import argparse

from utils import *
from update_comments import update_comments

api_key = os.getenv("KEY_API")
# video_ids = [os.getenv("VIDEO_ID_1"), os.getenv("VIDEO_ID_2")]
video_ids = [os.getenv("VIDEO_ID_1")]
youtube_owner_name = os.getenv("TF_VAR_NAME")

# def parse_arguments():
#     parser = argparse.ArgumentParser(description="Youtube comments analyzer")
#     parser.add_argument("--videos", required=True, nargs='+', help="Video(s) comment(s) to be analyzed. Please enter python3 get_comments.py --videos XXX YYY ZZZ")
#     return parser.parse_args()

if __name__ == "__main__":
    # args = parse_arguments()
    # video_ids = args.videos
    # print(f"video IDs : {video_ids}")
    first_upload_to_gcs(youtube_owner_name, video_ids, api_key)
    