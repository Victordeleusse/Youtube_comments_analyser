from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
)
import glob
import os
import chromadb
from typing import List
from langchain_core.documents import Document
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

from database_functions import *
from run_ollama_analysis import *


# embedding_model_name = os.getenv("BASE_EMBEDDING_MODEL")

def load_documents_from_Files(path: str) -> List[Document]:
    """
    Loads documents from the specified directory path, checking if they are already processed.

    Args:
        path (str): The path to the directory containing documents to load.
    Returns:
        dict: Dictionary of documents with their names as keys.
        List[str]: A list with their corresponding names in the folder.
    Raises:
        FileNotFoundError: If the specified path does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"The specified path does not exist: {path}")

    documents_names = []
    docs = []
    for file_path in glob.glob(os.path.join(path, '**', '*'), recursive=True):
        file_ext = os.path.splitext(file_path)[1].lower()
        document_name = os.path.basename(file_path)
        if document_name not in documents_names: 
            documents_names.append(document_name)
            document = None
            if file_ext in ['.pdf', '.txt']:  
                if file_ext == '.pdf':
                    loader = PyPDFLoader(file_path=file_path)
                else:
                    loader = TextLoader(file_path=file_path)

                document = loader.load()
                docs.append(document[0])
                
    return docs, documents_names

TEXT_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

def load_documents_into_database(embedding_model_name: str, documents_path: str):
    """
    Loads documents from the specified directory into the Chroma database
    after splitting the text into chunks.

    Returns:
        Chroma: The Chroma database with loaded documents.
    """

    documents_list, documents_names = load_documents_from_Files(documents_path)
    check_if_model_is_available(embedding_model_name)
    embeddings_model = OllamaEmbeddings(model=embedding_model_name)
    documents = TEXT_SPLITTER.split_documents(documents_list)
    
    print("Creating embeddings and loading documents into Chroma")
    
    db = Chroma.from_documents(
        documents,
        embeddings_model,
    )
    return db