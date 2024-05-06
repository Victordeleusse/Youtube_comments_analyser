from dotenv import load_dotenv
load_dotenv()
import os
from utils import first_upload_to_gcs
from database_functions import clear_table

api_key = os.getenv("KEY_API")
video_ids = [os.getenv("VIDEO_ID_1"), os.getenv("VIDEO_ID_2")]
youtube_owner_name = os.getenv("TF_VAR_NAME")

if __name__ == "__main__":
    # clear_table('videos_table')
    # clear_table('bad_comments_table')
    # clear_table('bad_viewers')
    first_upload_to_gcs(youtube_owner_name, video_ids, api_key)
    