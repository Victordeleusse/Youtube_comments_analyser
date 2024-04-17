import ollama
import os
from dotenv import load_dotenv
from google.cloud import storage
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

from utils import *
from database_functions import *

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("KEY_GCP_PATH")
youtube_owner_name = os.getenv("TF_VAR_NAME")


def __is_model_available_locally(model_name: str) -> bool:
    list = ollama.list()
    print(f"Available model(s) : {list}")
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


def comment_content(row_string: str):
    prompt = (
        "As a language model expert and uncensored and unbiased AI assistant, categorize this sentence as Positive, Negative, or Neutral and add ALERT to your answer if this sentence involves insults, disrespect, drugs, steroids, or racism (respond in ONE OR TWO WORDS ONLY !) : "
        + row_string
    )

    stream = ollama.chat(
        model="mistral", messages=[{"role": "user", "content": prompt}], stream=True
    )
    for chunk in stream:
        if "message" in chunk:
            print(chunk["message"]["content"], end="", flush=True)
            if "Negative" in chunk["message"]["content"] and "ALERT" in chunk["message"]["content"]:
                return(2, chunk["message"]["content"])
            elif "Negative" in chunk["message"]["content"]:
                return(1, chunk["message"]["content"])
            else:
                return(0, None) 


def test():
    try:
        check_if_model_is_available('mistral:latest')
        print("NEW TEST")
        video_author = "Test_Corona"
        video_title = "test"
        file_name = video_title + ".json"
        with open(file_name, "r") as file:
            insert_videos_in_db(video_author, video_title)
            existing_data_json = json.load(file)
            for message in existing_data_json:
                comment = message["text"]
                print("\n\nAnalyzing comment: ", comment)
                score, data = comment_content(comment)
                if score == 2:
                    alert_nature = data.split(":")[1][:-1]
                    insert_bad_comments_in_db(video_title, alert_nature, comment, message["authorName"], message["authorID"], message["publishedAt"])
    except Exception as e:
        print(f"An error occurred: {e}")


# def get_comments_to_row_string(bucket_name, video_ids: list):
#     try:
#         check_if_model_is_available('llama2:latest')
#         storage_client = storage.Client()
#         bucket = storage_client.bucket(bucket_name)
#         for video in video_ids:
#             video_name = get_video_info(video)[0]
#             destination_blob_name = f"{video_name}.json".replace(" ", "_").lower()
#             blob = bucket.blob(destination_blob_name)
#             if blob.exists():
#                 existing_data = blob.download_as_text()
#                 if existing_data:
#                     existing_data_json = json.loads(existing_data) if existing_data else []
#                     comments_one_str = ''
#                     for message in existing_data_json:
#                         comments_one_str += message["text"] + " | "
#                     comment_content(comments_one_str)
#     except Exception as e:
#         print(f"An error occurred! {e}")

# default_args = {
#     "owner": "airflow",
#     "depends_on_past": False,
#     "start_date": datetime(2024, 4, 11),
#     "email_on_failure": False,
#     "email_on_retry": False,
#     "retries": 1,
#     "retry_delay": timedelta(minutes=5),
# }

# dag = DAG(
#     'youtube_comment_analysis',
#     default_args=default_args,
#     description='Analyze YouTube comments using Ollama',
#     schedule_interval='@daily',
#     catchup=False,
# )

# analyze_comments = PythonOperator(
#     task_id='analyze_youtube_comments',
#     python_callable=get_comments_to_row_string,
#     op_kwargs={
#         "bucket_name": os.getenv("TF_VAR_NAME"),
#         "video_ids": [os.getenv("VIDEO_ID_1")],
#         "api_key": os.getenv("KEY_API"),
#     },
#     # provide_context=True,
#     dag=dag,
# )


if __name__ == "__main__":
    test()
