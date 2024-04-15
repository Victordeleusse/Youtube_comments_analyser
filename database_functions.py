import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

load_dotenv()

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')

POSTGRES_DB_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

def connect_to_db():
    try:
        connector = psycopg2.connect(POSTGRES_DB_URL)
        return connector
    except Exception as e:
        print(f"An error as occured when trying to connect to the db : {e}")
        return None

def insert_videos_in_db(video_author: str, video_title: str):
    try:
        connector = connect_to_db()
        cursor = connector.cursor()
        table_name = 'videos_table'
        query_table_exist = f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}')"
        cursor.execute(query_table_exist)
        table_exists = cursor.fetchone()[0]
        if table_exists:
            print(f"Table '{table_name}' already exist in database.")
        else:
            print(f"Table '{table_name}' doesn't exist, let's generate it.")
            query_create = f"CREATE TABLE {table_name} (video_id SERIAL PRIMARY KEY, video_author TEXT NOT NULL, video_title TEXT NOT NULL)"
            cursor.execute(query_create)
        query_video_already_in_table = f"SELECT COUNT(*) FROM {table_name} WHERE video_title = {video_title}"
        count = cursor.execute(query_video_already_in_table)
        if count > 0:
            return
        query_insert = f"INSERT INTO {table_name} VALUES {video_author} {video_title}"
        cursor.execute(query_insert)
    except Exception as e:
        print(f"An error as occured when trying to insert video in the db : {e}")
        return None

def insert_bad_comments_in_db(video_title: str, alertNature: str, text: str, authorName: str, authorID: str, publishedAt: str):
    try:
        connector = connect_to_db()
        cursor = connector.cursor()
        table_name = 'bad_comments_table'
        query_table_exist = f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}')"
        cursor.execute(query_table_exist)
        table_exists = cursor.fetchone()[0]
        if table_exists:
            print(f"Table '{table_name}' already exist in database.")
        else:
            print(f"Table '{table_name}' doesn't exist, let's generate it.")
            query_create = f"CREATE TABLE {table_name} (comment_id SERIAL PRIMARY KEY, video_title TEXT NOT NULL, alertNature TEXT NOT NULL, text TEXT NOT NULL, authorName TEXT NOT NULL, authorID TEXT NOT NULL, publishedAt TEXT NOT NULL, FOREIGN KEY (video_title) REFERENCES videos_table(video_title))"
            cursor.execute(query_create)
        query_insert = f"INSERT INTO {table_name} VALUES {video_title} {alertNature} {text} {authorName} {authorID} {publishedAt}"
        cursor.execute(query_insert)
    except Exception as e:
        print(f"An error as occured when trying to insert bad comment in the db : {e}")
        return None
    
def handle_bad_viewer_in_db(cursor, authorName, authorID):
    table_name = 'bad_viewers_table'
    query_table_exist = f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}')"
    cursor.execute(query_table_exist)
    table_exists = cursor.fetchone()[0]
    if table_exists:
        print(f"Table '{table_name}' already exist in database.")
    else:
        print(f"Table '{table_name}' doesn't exist, let's generate it.")
        query_create = f"CREATE TABLE {table_name} (viewer_id SERIAL PRIMARY KEY, authorName TEXT NOT NULL, authorID TEXT NOT NULL, badCommentsCount INT, FOREIGN KEY (authorName) REFERENCES bad_comments_table(authorName))"
        cursor.execute(query_create)
    query_bad_viewer_exist = f"SELECT * FROM {table_name} WHERE authorName = {authorName})"
    is_present = cursor.execute(query_bad_viewer_exist)
    if is_present:
        query_update_bad_viewer