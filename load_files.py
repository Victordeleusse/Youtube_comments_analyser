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

def load_documents_from_Files(path: str):
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
    docs = {}
    for file_path in glob.glob(os.path.join(path, '**', '*'), recursive=True):
        file_ext = os.path.splitext(file_path)[1].lower()
        document_name = os.path.basename(file_path)
        if document_name not in documents_names: 
            documents_names.append(document_name)
            # Check if document has already been processed
            if not check_doc_in_db(document_name):
                document = None
                if file_ext in ['.pdf', '.txt']:  
                    if file_ext == '.pdf':
                        loader = PyPDFLoader(file_path=file_path)
                    else:
                        loader = TextLoader(file_path=file_path)

                    document = loader.load()
                    text_content = ""
                    # print(f"DOCUMENT : {document}")
                    # print(f"DOCUMENT INFO : {dir(document)}")
                    if isinstance(document, list):
                        for doc in document:
                            # document = ' '.join(doc.text if isinstance(doc, Document) else doc for doc in document)
                            print(doc.page_content)
                            print(type(doc.page_content))
                            
                            text_content += doc.page_content
                    elif hasattr(document, 'page_content'):
                        text_content.append(document.page_content)
                    elif isinstance(document, Document):
                        document.text
                    elif isinstance(document, bytes):
                        document = document.decode('utf-8')
                    # document_full_text = ' '.join(text_content)
                    if isinstance(text_content, str):
                        docs[document_name] = text_content
                    else:
                        print(f"No text content extracted from {document_name}.")

    return docs, documents_names


TEXT_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

def load_documents_into_database(embedding_model_name: str, documents_path: str):
    """
    Loads documents from the specified directory into the Chroma database
    after splitting the text into chunks.

    Returns:
        Chroma: The Chroma database with loaded documents.
    """

    raw_documents_dic, all_documents_names = load_documents_from_Files(documents_path)
    check_if_model_is_available(embedding_model_name)
    embeddings_model = OllamaEmbeddings(model=embedding_model_name)
    # print(embeddings_model)

    print("Creating embeddings and loading documents into our db")
    for document_name, document in raw_documents_dic.items():
        document_splitted = TEXT_SPLITTER.split_text(document) 
        document_embeddings = []
        print("Creating embeddings")
        for chunk in document_splitted:
            print(chunk)
            embedding = embeddings_model.embed_query(chunk)
            document_embeddings.append(embedding)

        # Combine embeddings (e.g., by averaging)
        combined_embedding = np.mean(document_embeddings, axis=0)
        print("Loading")
        insert_embedded_documents_in_db(document_name, combined_embedding.tolist())

    
    embedded_vectors = get_embedded_docs(all_documents_names)
    
    # db = Chroma.from_documents(
    #     embedded_vectors,
    #     OllamaEmbeddings(model=embedding_model_name),
    # )
    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="my_collection")
        
    collection.add(
        ids=all_documents_names,
        embeddings=embedded_vectors,
    )
    # documents=["This is a document", "This is another document"],
    # metadatas=[{"source": "my_source"}, {"source": "my_source"}],
    # ids=["id1", "id2"]
    # )
    
    return collection