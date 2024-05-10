import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
# import numpy as np

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
                cursor.execute(sql.SQL("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)"),[table_name])
                table_exists = cursor.fetchone()[0]
                if table_exists:
                    cursor.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name)))
                    rows = cursor.fetchall()
                    for row in rows:
                        print(row)
                    cursor.close()
                else:
                    print(f"Table {table_name} doesn't exist.")
            # conn.close()
    except Exception as e:
        print(f"An error as occured when reading {table_name} in the database : {e}")

def clear_table(table_name: str):
    try:
        with connect_to_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql.SQL("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)"),[table_name])
                table_exists = cursor.fetchone()[0]
                if table_exists:
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
                        "SELECT COUNT(*) FROM {} WHERE video_title = %s AND authorName = %s AND text = %s"
                    ).format(sql.Identifier(table_name)),
                    [video_title, authorName, text],
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
        

def extract_for_result():
    try:
        with connect_to_db() as conn:
            with conn.cursor() as cursor:
                table_name_b = "bad_comments_table"
                cursor.execute(sql.SQL("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)"), [table_name_b])
                table_exists = cursor.fetchone()[0]
                if not table_exists:
                    print(f"Table {table_name_b} doesn't exist : No bad viewrs.")
                    return
                query = sql.SQL("""
                    SELECT
                        b.authorname,
                        b.authorID,
                        bv.count,
                        array_agg(b.video_title) AS video_titles,
                        array_agg(b.alertNature) AS alertNatures,
                        array_agg(b.text) AS texts,
                        array_agg(b.publishedAt) AS publishedAts
                    FROM
                        {table_b} b
                    INNER JOIN
                        {table_bv} bv
                    ON
                        b.authorName = bv.authorName AND b.authorID = bv.authorID
                    GROUP BY
                        b.authorname, b.authorID, bv.count
                                """).format(table_b=sql.Identifier('bad_comments_table'), table_bv=sql.Identifier('bad_viewers'))
                cursor.execute(query=query)
                return cursor.fetchall()
    except Exception as e:
        print(f"An error occurred when trying to extract results from db: {e}")
        
def get_result_in_pdf():
    # pdf = SimpleDocTemplate('result.pdf', pagesize=letter)
    pdf = SimpleDocTemplate('result.pdf', pagesize=letter, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    elements = []
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleN.fontSize = 8
    styleN.wordWrap = 'CJK'
    
    data = extract_for_result()
    if not data:
        print("No data returned from tables extraction.")
        return
    columns = ['Author', 'Author ID', 'Count', 'Video', 'Alert', 'Comment', 'Published at']
    dataframe = pd.DataFrame(data=data, columns=columns)
    # print(f"Dataframe HEAD : {dataframe.head()}")
    
    data_for_table = []
    headers = [Paragraph('<b>{}</b>'.format(str(col)), styles['Heading4']) for col in columns]
    data_for_table.append(headers)
    
    for idx, row in dataframe.iterrows():
        row_data = [Paragraph(str(item), styleN) if not isinstance(item, list) else Paragraph('<br/>'.join(str(x) for x in item), styleN) for item in row]
        data_for_table.append(row_data)
    
    # print(f"Data for table : \n{data_for_table[:2]}")
    # def custom_str(item):
    #     if isinstance(item, list):
    #         return ', '.join(map(str, item))
    #     return str(item)
    
    # data = [[Paragraph(custom_str(item), styleN) if isinstance(item, str) else item for item in row] for row in dataframe.values]
    # data.insert(0, [Paragraph('<b>{}</b>'.format(str(col)), styles['Heading4']) for col in dataframe.columns])  # Entêtes de colonnes

    table = Table(data_for_table, colWidths=[100, 100, 30, 100, 50, 140, 60])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#d3d3d3'),
        ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, 'black'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(table)
    pdf.build(elements)
    
if __name__ == "__main__":
    get_result_in_pdf()