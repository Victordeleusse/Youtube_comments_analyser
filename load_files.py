from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
)
import os
from typing import List
from langchain_core.documents import Document
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

from database_functions import *

embedding_model_name = [os.getenv("BASE_EMBEDDING_MODEL")]


def load_documents_from_Files(path: str):
    """
    Loads documents from the specified directory path.
    You will then be able to enter specific contexts you want to ban from your channel

    Args:
        path (str): The path to the directory containing documents to load.
    Returns:
        List[Document]: A list of loaded documents.
        List[str]: A list with their corresponding names in the folder.
    Raises:
        FileNotFoundError: If the specified path does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"The specified path does not exist: {path}")

    loaders = {
        ".pdf": DirectoryLoader(
            path,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True,
            use_multithreading=True,
        ),
        ".md": DirectoryLoader(
            path,
            glob="**/*.md",
            loader_cls=TextLoader,
            show_progress=True,
        ),
    }
    documents_names = []
    docs = {}
    for file_type, loader in loaders.items():
        print(f"Loading {file_type} files")
        file_list = loader.file_list()
        for file_path in file_list:
            document_name = os.path.basename(file_path)
            documents_names.append(document_name)
            already_process = check_doc_in_db(document_name)
            if not already_process:
                document = loader.load(file_path)
                docs[document_name] = document
    return docs, documents_names


TEXT_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

def load_documents_into_database(
    embedding_model_name: str, documents_path: str
) -> Chroma:
    """
    Loads documents from the specified directory into the Chroma database
    after splitting the text into chunks.

    Returns:
        Chroma: The Chroma database with loaded documents.
    """

    raw_documents_dic, all_documents_names = load_documents_from_Files(documents_path)
    embeddings_model = OllamaEmbeddings(model=embedding_model_name)

    print("Creating embeddings and loading documents into our db")
    for document_name, document in raw_documents_dic.items():
        document_splitted = TEXT_SPLITTER.split_text(document['content'])  # Ensure document is split correctly
        document_embeddings = []
        for chunk in document_splitted:
            embedding = embeddings_model.embed_text(chunk)
            document_embeddings.append(embedding)

        # Combine embeddings (e.g., by averaging)
        combined_embedding = np.mean(document_embeddings, axis=0)
        insert_embedded_documents_in_db(document_name, combined_embedding.tolist())

    
    embedded_vectors = get_embedded_docs(all_documents_names)
    
    db = Chroma.from_documents(
        embedded_vectors,
        OllamaEmbeddings(model=embedding_model_name),
    )
    return db
