import os
from dotenv import load_dotenv
from google.cloud import storage
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from utils import *

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("KEY_GCP_PATH")
api_key = os.getenv("KEY_API")
youtube_owner_name = os.getenv("TF_VAR_NAME")

# The XComs allow tasks to communicate with each other by exchanging small pieces of data.
def append_to_blob(youtube_owner_name, new_data: dict):
    storage_client = storage.Client()
    bucket = storage_client.bucket(youtube_owner_name)
    for video_name, new_video_comments in new_data.items():
        if new_video_comments:
            blob_name = f"{video_name}.json".replace(" ", "_").lower()
            blob = bucket.blob(blob_name)
            # context['task_instance'].xcom_push(key=blob_name, value=blob_name)
            existing_data = blob.download_as_text()
            existing_data_json = json.loads(existing_data) if existing_data else []
            existing_data_json.extend([message.__dict__ for message in new_video_comments])
            updated_data = json.dumps(existing_data_json, ensure_ascii=False).encode('utf-8')
            blob.upload_from_string(updated_data, content_type="application/json")
            print(f"Blob {blob_name} in the bucket {youtube_owner_name} has been updated with new data.")

def update_comments(bucket_name, video_ids: list, api_key: str):
    try:
        videos_messages = load_comments(bucket_name, video_ids, api_key)
        lw_messages = select_day_comments(videos_messages)
        # return(lw_messages)
        append_to_blob(youtube_owner_name, lw_messages)
    except Exception as e:
        print(f"An error occurred! {e}")
    pass

# def load_comments_from_blob(bucket_name, blob_name):
#     storage_client = storage.Client()
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(blob_name)
#     data = json.loads(blob.download_as_string())
#     return [comment["text"] for comment in data]

# def analyze_sentiment_for_text(text):
#     client = language_v1.LanguageServiceClient()
#     document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
#     sentiment = client.analyze_sentiment(request={'document': document}).document_sentiment
#     return sentiment.score

# def analyze_overall_sentiment(bucket_name, **context):
#     blob_names = context['task_instance'].xcom_pull(task_ids='update_comments')
#     storage_client = storage.Client()
#     bucket = storage_client.bucket(bucket_name)
#     blob_result = bucket.blob("result")
#     if blob_result.exists():
#         blob_result.delete()
#     sentiments_results = {}
#     for blob_name in blob_names:
#         comments = load_comments_from_blob(bucket_name, blob_name)
#         sentiment_scores = [analyze_sentiment_for_text(comment) for comment in comments]
#         video_name = ' '.join(blob_name.split('.')[0].split('_')).capitalize()
#         if sentiment_scores:
#             average_sentiment = sum(sentiment_scores) / len(sentiment_scores)
#             sentiments_results[video_name] = average_sentiment
#         else:
#             sentiments_results[video_name] = "No comment to analyse."
#     storage_client = storage.Client()
#     bucket = storage_client.bucket(bucket_name)
#     blob_result = bucket.blob("result")
#     blob_result.upload_from_string(json.dumps(sentiments_results), content_type='application/json')


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
    "update_youtube_comments",
    default_args=default_args,
    description="Update YouTube comments daily",
    schedule_interval="@daily",
    # schedule_interval="*/30 * * * *",
    catchup=False,
)

t1 = PythonOperator(
    task_id="update_comments",
    python_callable=update_comments,
    op_kwargs={
        # "video_ids": [os.getenv("VIDEO_ID_1"), os.getenv("VIDEO_ID_2")],
        "bucket_name": os.getenv("TF_VAR_NAME"),
        "video_ids": [os.getenv("VIDEO_ID_1")],
        "api_key": os.getenv("KEY_API"),
    },
    provide_context=True,
    dag=dag,
)

# t2 = PythonOperator(
#     task_id="analyze_sentiment",
#     python_callable=analyze_overall_sentiment,
#     op_kwargs={"bucket_name": youtube_owner_name},
#     provide_context=True,
#     dag=dag,
# )

# t1 >> t2

# if __name__ == "__main__":
#     videos_list = [os.getenv("VIDEO_ID_1"), os.getenv("VIDEO_ID_2")]
#     key = os.getenv("KEY_API")
#     last_day_messages = update_comments(videos_list, api_key)
#     for name, messages_lst in last_day_messages.items():
#         for message in messages_lst:
#             print(message.authorName)
#             print(message.publishedAt)
