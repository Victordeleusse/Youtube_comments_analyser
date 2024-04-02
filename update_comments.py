import os
from dotenv import load_dotenv
from google.cloud import storage
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from utils import *

load_dotenv()
api_key = os.getenv("KEY_API")
youtube_owner_name = os.getenv("TF_VAR_NAME")

def append_to_blob(youtube_owner_name, new_data: dict):
    storage_client = storage.Client()
    bucket = storage_client.bucket(youtube_owner_name)
    for video_name, new_video_comments in new_data.items():
        if new_video_comments:
            blob_name = f"{video_name}.json".replace(" ", "_").lower()
            blob = bucket.blob(blob_name)
            existing_data = blob.download_as_text()
            existing_data_json = json.loads(existing_data) if existing_data else []
            new_video_comments = json.dumps([message.__dict__ for message in new_video_comments])
            existing_data_json.append(new_video_comments)
            updated_data = json.dumps(existing_data_json)
            blob.upload_from_string(updated_data, content_type='application/json')
    print(f"Blob {blob_name} in the bucket {youtube_owner_name} has been updated with new data.")

def update_comments(video_ids: list, api_key: str):
    try:
        videos_messages = load_comments(video_ids, api_key)
        lw_messages = select_day_comments(videos_messages)
        # return lw_messages
        append_to_blob(youtube_owner_name, lw_messages)
    except Exception as e:
        print(f"An error occurred! {e}")
    pass

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 4, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'update_youtube_comments',
    default_args=default_args,
    description='Update YouTube comments daily',
    # schedule_interval=timedelta(day=7),
    schedule_interval='*/30 * * * *',
)

t1 = PythonOperator(
    task_id='update_comments',
    python_callable=update_comments,
    op_kwargs={'video_ids': [os.getenv("VIDEO_ID_1"), os.getenv("VIDEO_ID_2")], 'api_key': os.getenv("KEY_API")},
    dag=dag,
)
