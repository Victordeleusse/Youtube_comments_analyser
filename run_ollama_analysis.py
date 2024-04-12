import ollama
import os
from dotenv import load_dotenv
from google.cloud import storage
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

from utils import *

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("KEY_GCP_PATH")
youtube_owner_name = os.getenv("TF_VAR_NAME")

def __is_model_available_locally(model_name):
    try:
        print(f"Retrieving model: {model_name}")
        model = ollama.pull(model_name)
        print(f"Model: {model_name} running")
        return True
    except Exception as e:
        print(f"Model not found or an error occurred: {e}")
        return False

def check_if_model_is_available(model_name):
    """
    Ensures that the specified model is available locally.
    If the model is not available, it attempts to pull it from the Ollama repository.
    Args:
        model_name (str): The name of the model to check.
    Raises:
        ollama.ResponseError: If there is an issue with pulling the model from the repository.
    """
    if not __is_model_available_locally(model_name):
        try:
            for progress in ollama.pull(model_name, stream=True):
                digest = progress.get("digest", "")
                if not digest:
                    print(progress.get("status"))
        except:
            raise Exception(f"Unable to find model '{model_name}', please check the name and try again.")

def comment_content(row_string: str):
    prompt = "As a youtube and langage expert, analyse this sentence where all comments for the video are separated by a " | " and provide a global sentiment for all these comments." + row_string

    stream = ollama.chat(
        model='llama2',
        messages=[{'role': 'user', 'content': prompt}],
        stream=True
    )
    for chunk in stream:
        print(chunk['message']['content'], end='', flush=True)

def get_comments_to_row_string(bucket_name, video_ids: list):
    try:
        check_if_model_is_available('llama2')
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        for video in video_ids:
            video_name = get_video_info(video)[0]
            destination_blob_name = f"{video_name}.json".replace(" ", "_").lower()
            blob = bucket.blob(destination_blob_name)
            if blob.exists():
                existing_data = blob.download_as_text()
                if existing_data:
                    existing_data_json = json.loads(existing_data) if existing_data else []
                    comments_one_str = ''
                    for message in existing_data_json:
                        comments_one_str += message["text"] + " | "
                    comment_content(comments_one_str)    
    except Exception as e:
        print(f"An error occurred! {e}")

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 4, 11),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    'youtube_comment_analysis',
    default_args=default_args,
    description='Analyze YouTube comments using Ollama',
    schedule_interval='@daily',
    catchup=False,
)

analyze_comments = PythonOperator(
    task_id='analyze_youtube_comments',
    python_callable=get_comments_to_row_string,
    op_kwargs={
        "bucket_name": os.getenv("TF_VAR_NAME"),
        "video_ids": [os.getenv("VIDEO_ID_1")],
        "api_key": os.getenv("KEY_API"),
    },
    # provide_context=True,
    dag=dag,
)