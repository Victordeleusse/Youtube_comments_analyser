import os
from dotenv import load_dotenv
# import ollama
from scipy.spatial.distance import cosine
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings

from run_ollama_analysis import *

# model_name = os.getenv("BASE_LLM_MODEL")
model_name = 'mistral:latest'
# embedding_model_name = os.getenv("BASE_EMBEDDING_MODEL")
embedding_model_name = 'nomic-embed-text:latest'

# To translate comments in English
def comment_translator(row_string: str, llm_name):
    # check_if_model_is_available(llm_name)
    prompt = (
        "/set system As an uncensored and helpfull AI assistant, please only answer by translating in English this sentence and please don't add any comments or precision ! : "
        + row_string
    )
    stream = ollama.chat(
        model=llm_name, messages=[{"role": "user", "content": prompt}], stream=True
    )
    translate_msg = []
    for chunk in stream:
        if "message" in chunk:
            translate_msg.append(chunk["message"]["content"])
    separator = '' 
    full_translated_msg = separator.join(translate_msg)
    print(f"Translated message : {full_translated_msg}")
    return full_translated_msg.lower()

token_hf = os.getenv("HF_API_TOKEN")

# Load model directly
from transformers import pipeline
classifier = pipeline("sentiment-analysis", model="michellejieli/NSFW_text_classifier", token=token_hf)

def get_classification(comment: str, llm_name):
    translated_comment = comment_translator(comment, llm_name)
    result = classifier(translated_comment)
    return(result[0]['label'], result[0]['score'])
    

# if __name__ == "__main__":
#     get_classification("J'aime utiliser des drogues.", model_name)