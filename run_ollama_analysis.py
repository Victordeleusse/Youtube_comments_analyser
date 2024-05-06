import ollama
import os
from dotenv import load_dotenv
from google.cloud import storage
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta, date

from utils import *
from database_functions import *
from classify_comment import *

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("KEY_GCP_PATH")
video_ids = [os.getenv("VIDEO_ID_1"), os.getenv("VIDEO_ID_2")]
model_name = os.getenv("BASE_LLM_MODEL")
embedding_model_name = os.getenv("BASE_EMBEDDING_MODEL")


youtube_owner_name = os.getenv("TF_VAR_NAME")

def __is_model_available_locally(model_name: str) -> bool:
    list = ollama.list()
    # print(f"Available model(s) : {list}")
    if list:
        models = []
        for model in list["models"]:
            models.append(model["model"])
        if model_name in models:
            return True
    return False


def check_if_model_is_available(model_name: str) -> None:
    available = __is_model_available_locally(model_name)
    if available == False:
        print(f"Let s pull the model {model_name} first.")
        ollama.pull(model_name)
    else:
        print(f"The model {model_name} is already present locally.")


def alert_comment_detector(bucket_name, video_ids: list):
    try:
        # clear_table('videos_table')
        # clear_table('bad_comments_table')
        # clear_table('bad_viewers')
        # check_if_model_is_available(embedding_model_name)
        # check_if_model_is_available(model_name)
        
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        for video in video_ids:
            video_name = get_video_info(video)[0]
            if (len(video_name)> 25):
                video_name = video_name[:25]
            destination_blob_name = f"{video_name}.json".replace(" ", "_").lower()
            blob = bucket.blob(destination_blob_name)
            if blob.exists():
                print("Downloading data from Cloud.")
                existing_data = blob.download_as_text()
                existing_data_json = json.loads(existing_data)
                insert_videos_in_db(youtube_owner_name, video_name)
                for message in existing_data_json:
                    comment = message["text"]
                    print("\n\nAnalyzing comment: ", comment)
                    # splited_translated_comment = comment_translator(comment, model_name)
                    splited_translated_comment = get_comment_translated(comment)
                    for translated_comment in splited_translated_comment:
                        res_label = get_label_classification(translated_comment)
                        label = res_label[0]
                        score = res_label[1]
                        print(f"LABEL : {label} / SCORE : {score}")
                        if score > 0.7:
                            print(f"ALERT NATURE : {label}")
                            alert_nature = label
                            author = message["authorName"]
                            print(f"AUTHOR : {author}")
                            insert_bad_comments_in_db(video_name, alert_nature, comment, message["authorName"], message["authorID"], message["publishedAt"])
                            break
                        else:
                            offensive = get_offense_classification(translated_comment)
                            print(f"ALERT NATURE : {offensive}")
                            if offensive == 'offensive':
                                print(f"ALERT NATURE : {offensive}")
                                alert_nature = offensive
                                author = message["authorName"]
                                print(f"AUTHOR : {author}")
                                insert_bad_comments_in_db(video_name, alert_nature, comment, message["authorName"], message["authorID"], message["publishedAt"])
                                break
            else:
                print(f"Blob {destination_blob_name} not found")               
    except Exception as e:
        print(f"An error occurred: {e}")
        
def daily_alert_comment_detector(bucket_name, video_ids: list):
    try:
        # clear_table('videos_table')
        # clear_table('bad_comments_table')
        # clear_table('bad_viewers')
        # check_if_model_is_available(embedding_model_name)
        # check_if_model_is_available(model_name)
        today = date.today()
        today = today.strftime("%Y-%m-%d")
        
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        for video in video_ids:
            video_name = get_video_info(video)[0]
            if (len(video_name)> 25):
                video_name = video_name[:25]
            destination_blob_name = f"{video_name}.json".replace(" ", "_").lower()
            blob = bucket.blob(destination_blob_name)
            if blob.exists():
                print("Downloading data from Cloud.")
                existing_data = blob.download_as_text()
                existing_data_json = json.loads(existing_data)
                insert_videos_in_db(youtube_owner_name, video_name)
                for message in existing_data_json:
                    publishedAt = message["publishedAt"]
                    if publishedAt == today:
                        comment = message["text"]
                        print("\n\nAnalyzing comment: ", comment)
                        # splited_translated_comment = comment_translator(comment, model_name)
                        splited_translated_comment = get_comment_translated(comment)
                        for translated_comment in splited_translated_comment:
                            res_label = get_label_classification(translated_comment)
                            label = res_label[0]
                            score = res_label[1]
                            print(f"LABEL : {label} / SCORE : {score}")
                            if score > 0.7:
                                print(f"ALERT NATURE : {label}")
                                alert_nature = label
                                author = message["authorName"]
                                print(f"AUTHOR : {author}")
                                insert_bad_comments_in_db(video_name, alert_nature, comment, message["authorName"], message["authorID"], message["publishedAt"])
                                break
                            else:
                                offensive = get_offense_classification(translated_comment)
                                print(f"ALERT NATURE : {offensive}")
                                if offensive == 'offensive':
                                    print(f"ALERT NATURE : {offensive}")
                                    alert_nature = offensive
                                    author = message["authorName"]
                                    print(f"AUTHOR : {author}")
                                    insert_bad_comments_in_db(video_name, alert_nature, comment, message["authorName"], message["authorID"], message["publishedAt"])
                                    break
            else:
                print(f"Blob {destination_blob_name} not found")               
    except Exception as e:
        print(f"An error occurred: {e}")


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
    description='Analyze YouTube comments',
    schedule_interval='@daily',
    catchup=False,
)

t1 = PythonOperator(
    task_id='analyze_youtube_comments',
    python_callable=daily_alert_comment_detector,
    op_kwargs={
        "bucket_name": os.getenv("TF_VAR_NAME"),
        "video_ids": [os.getenv("VIDEO_ID_1"), os.getenv("VIDEO_ID_2")],
    },
    provide_context=True,
    dag=dag,
)


if __name__ == "__main__":
    print("Launching ... \n ")
    # alert_comment_detector(youtube_owner_name, video_ids)
    daily_alert_comment_detector(youtube_owner_name, video_ids)
    print(f"\n videos_table \n")
    read_table('videos_table')
    print(f"\n bad_comments_table \n")
    read_table('bad_comments_table')
    print(f"\n bad_viewers \n")
    read_table('bad_viewers')
    print("Launching ... \n ")
    

