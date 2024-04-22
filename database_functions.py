import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
import numpy as np

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

POSTGRES_DB_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


def connect_to_db():
    try:
        connector = psycopg2.connect(POSTGRES_DB_URL)
        return connector
    except Exception as e:
        print(f"An error as occured when trying to connect to the db : {e}")
        return None
    
def read_table(table_name: str):
    try:
        with connect_to_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name)))
                rows = cursor.fetchall()
                for row in rows:
                    print(row)
                cursor.close()
            # conn.close()
    except Exception as e:
        print(f"An error as occured when reading {table_name} in the database : {e}")

def clear_table(table_name: str):
    try:
        with connect_to_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql.SQL("DELETE FROM {}").format(sql.Identifier(table_name)))
                cursor.close()
            # conn.close()
    except Exception as e:
        print(f"An error as occured when deleting data from {table_name} in the database : {e}")

def insert_videos_in_db(video_author: str, video_title: str):
    try:
        with connect_to_db() as conn:
            with conn.cursor() as cursor:
                table_name = "videos_table"
                # Check if table exists
                cursor.execute(
                    sql.SQL(
                        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)"
                    ),
                    [table_name],
                )
                table_exists = cursor.fetchone()[0]
                if not table_exists:
                    print(f"Table {table_name} doesn't exist, creating it.")
                    cursor.execute(
                        sql.SQL(
                            "CREATE TABLE {} (video_id INT PRIMARY KEY, video_author TEXT NOT NULL, video_title TEXT NOT NULL)"
                        ).format(sql.Identifier(table_name))
                    )
                # Check if the video already exists
                cursor.execute(
                    sql.SQL("SELECT COUNT(*) FROM {} WHERE video_title = %s").format(
                        sql.Identifier(table_name)
                    ),
                    [video_title],
                )
                if cursor.fetchone()[0] == 0:
                    cursor.execute(sql.SQL("SELECT MAX(video_id) FROM {}").format(sql.Identifier(table_name)))
                    result = cursor.fetchone()
                    previous_id = result[0] if result[0] is not None else 0
                    cursor.execute(
                        sql.SQL(
                            "INSERT INTO {} (video_id, video_author, video_title) VALUES (%s, %s, %s)"
                        ).format(sql.Identifier(table_name)),
                        [previous_id + 1, video_author, video_title],
                    )
                    print("Video inserted successfully.")
                else:
                    print("Video already exists in the database.")
                conn.commit()
    except Exception as e:
        print(f"An error occurred when inserting video into the db: {e}")
        conn.rollback()


def insert_bad_comments_in_db(
    video_title: str,
    alertNature: str,
    text: str,
    authorName: str,
    authorID: str,
    publishedAt: str,
):
    try:
        with connect_to_db() as conn:
            with conn.cursor() as cursor:
                table_name = "bad_comments_table"
                # Check if table exists
                cursor.execute(
                    sql.SQL(
                        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)"
                    ),
                    [table_name],
                )
                table_exists = cursor.fetchone()[0]
                if not table_exists:
                    print(f"Table {table_name} doesn't exist, creating it.")
                    cursor.execute(
                        sql.SQL(
                            "CREATE TABLE {} (comment_id INT PRIMARY KEY, video_title TEXT NOT NULL, alertNature TEXT NOT NULL, text TEXT NOT NULL, authorName TEXT NOT NULL, authorID TEXT NOT NULL, publishedAt TEXT NOT NULL)"
                        ).format(sql.Identifier(table_name))
                    )
                # Check if the comment already exists
                cursor.execute(
                    sql.SQL(
                        "SELECT COUNT(*) FROM {} WHERE video_title = %s AND authorName = %s AND publishedAt = %s"
                    ).format(sql.Identifier(table_name)),
                    [video_title, authorName, publishedAt],
                )
                if cursor.fetchone()[0] == 0:
                    cursor.execute(sql.SQL(
                            "SELECT MAX(comment_id) FROM {}").format(sql.Identifier(table_name)))
                    result = cursor.fetchone()
                    previous_id = result[0] if result[0] is not None else 0
                    cursor.execute(
                        sql.SQL(
                            "INSERT INTO {} (comment_id, video_title, alertNature, text, authorName, authorID, publishedAt) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                        ).format(sql.Identifier(table_name)),
                        [
                            previous_id + 1,
                            video_title,
                            alertNature,
                            text,
                            authorName,
                            authorID,
                            publishedAt,
                        ],
                    )
                    print("Comment has been added to the database.")
                    handle_bad_viewer_in_db(cursor, authorName, authorID)
                else:
                    print("Comment already exists in the database.")
                conn.commit()
    except Exception as e:
        print(f"An error occurred with bad comment: {e}")
        if conn:
            conn.rollback()


def handle_bad_viewer_in_db(cursor, authorName: str, authorID: str):
    try:
        table_name = "bad_viewers"
        cursor.execute(sql.SQL("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)"), [table_name])
        table_exists = cursor.fetchone()[0]
        if not table_exists:
            cursor.execute(sql.SQL("CREATE TABLE {} (bad_viewer_id INT PRIMARY KEY, authorName TEXT NOT NULL, authorID TEXT NOT NULL, count INT)").format(sql.Identifier(table_name)))
            print(f"Table {table_name} created.")

        cursor.execute(sql.SQL("SELECT count FROM {} WHERE authorName = %s").format(sql.Identifier(table_name)), [authorName])
        result = cursor.fetchone()
        if result:
            new_count = result[0] + 1
            cursor.execute(sql.SQL("UPDATE {} SET count = %s WHERE authorName = %s").format(sql.Identifier(table_name)), [new_count, authorName])
        else:
            cursor.execute(sql.SQL("SELECT MAX(bad_viewer_id) FROM {}").format(sql.Identifier(table_name)))
            result = cursor.fetchone()
            previous_id = result[0] if result[0] is not None else 0
            cursor.execute(sql.SQL("INSERT INTO {} (bad_viewer_id, authorName, authorID, count) VALUES (%s, %s, %s, 1)").format(sql.Identifier(table_name)), [previous_id + 1, authorName, authorID])
        print("Bad viewer record updated in the database.")
    except Exception as e:
        print(f"An error occurred with bad viewer: {e}")
        

def check_doc_in_db(document_name):
    """
    Check if the document has already been stored after being embedded in the database.
    """
    try:
        with connect_to_db() as conn:
            with conn.cursor() as cur:
                # Check if table exists
                table_name = "embeddings"
                cur.execute(sql.SQL("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)"), [table_name])
                table_exists = cur.fetchone()[0]
                if not table_exists:
                    cur.execute(sql.SQL("CREATE TABLE {} (document_id INT PRIMARY KEY, document_name TEXT NOT NULL, embedding FLOAT8[])").format(sql.Identifier(table_name)))
                    print(f"Table {table_name} created.")
                    return False
                else:
                    cur.execute(sql.SQL("SELECT EXISTS (SELECT 1 FROM {} WHERE document_name = %s)").format(sql.Identifier(table_name)), [document_name])
                    return cur.fetchone()[0]
    except Exception as e:
        print(f"An error occurred when trying to access document name into the db: {e}")
    

def insert_embedded_documents_in_db(document_name, embedding):
    """
    Saves an embedding document to PostgreSQL database.
    Args:
        document_name (str).
        embedding (list): The embedding vector.
    """
    try:
        with connect_to_db() as conn:
            with conn.cursor() as cur:
                if isinstance(embedding, np.ndarray):
                    embedding = embedding.tolist()
                # Check if table exists
                table_name = "embeddings"
                # cur.execute(sql.SQL("SELECT EXIST (SELECT FROM information_schema.tables WHERE table_name = {})").format(sql.Identifier(table_name)))
                # table_exists = cur.fetchone()[0]
                # if not table_exists:
                #     cur.execute(sql.SQL("CREATE TABLE {} (document_id INT PRIMARY KEY, document_name TEXT NOT NULL, embedding FLOAT8[])").format(sql.Identifier(table_name)))
                #     print(f"Table {table_name} created.")
                #     max_index = 0
                # else:
                max_index = cur.execute(sql.SQL("SELECT MAX(document_id) FROM {}").format(sql.Identifier(table_name)))     
                if not max_index:
                    max_index = 0
                print(f"Document name : {document_name}")
                print(f"Data ready to embed : {embedding}")
                print(type(embedding))
                cur.execute(sql.SQL("INSERT INTO {} (document_id, document_name, embedding) VALUES (%s, %s, %s)").format(sql.Identifier(table_name)), (max_index + 1, document_name, embedding))
                conn.commit()
                print("Document and embedding inserted successfully.")
    except Exception as e:
        print(f"An error occurred with embeddings: {e}")
        

def get_embedded_docs(documents_names: list) -> list:
    try:
        with connect_to_db() as conn:
            with conn.cursor() as cur:
                table_name = "embeddings"
                cur.execute(sql.SQL("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)"), [table_name])
                table_exists = cur.fetchone()[0]
                if not table_exists:
                    print("Embeddings table does not exist.")
                    return None
                embedded_documents = []
                for document in documents_names:
                    cur.execute(sql.SQL("SELECT embedding FROM {} WHERE document_name = %s").format(sql.Identifier(table_name)), [document])
                    result = cur.fetchone()
                    if result:
                        embedded_documents.append(result[0])
                return embedded_documents
    except Exception as e:
        print(f"An error occurred when retrieving embeddings documents in the database: {e}")
        return None