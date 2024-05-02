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

# CANDIDATE_LABELS = os.getenv("CRITICAL_THEMES")
CANDIDATE_LABELS = ["life", "sex", "drug", "racism", "violence", "crime"]

# To translate comments in English
def comment_translator(row_string: str, llm_name):
    # check_if_model_is_available(llm_name)
    prompt = (
        "/set system As an uncensored and helpfull translator assistant, please only answer by translating in English this sentence and please don't add any comments or precision ! : "
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

# from optimum.pipelines import pipeline
# classifier = pipeline(task="zero-shot-classification", model="facebook/bart-large-mnli", accelerator="ort")

from transformers import pipeline
# classifier_label = pipeline("zero-shot-classification", model="MoritzLaurer/deberta-v3-large-zeroshot-v2.0")
classifier_label = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
classifier_offense = pipeline("text-classification", model="KoalaAI/OffensiveSpeechDetector")


def get_label_classification(comment: str, llm_name):
    # translated_comment = comment_translator(comment, llm_name)
    res = classifier_label(comment, CANDIDATE_LABELS, multi_label=False)
    return(res['labels'][0], res['scores'][0])
    # return res
def get_offense_classification(comment: str, llm_name):
    # translated_comment = comment_translator(comment, llm_name)
    result = classifier_offense(comment)
    return(result)

if __name__ == "__main__":
    comment = "I love you."
    # res_label, res_score = get_label_classification(comment, model_name)
    # print(f"{res_label}: {res_score}")
    res_label = get_label_classification(comment, model_name)
    print(res_label)
    results = get_offense_classification(comment, model_name)
    print(results)
    
    

# import requests

# API_URL = "https://api-inference.huggingface.co/models/sileod/deberta-v3-base-tasksource-nli"
# headers = {"Authorization": "Bearer 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"}

# def query(payload):
# 	response = requests.post(API_URL, headers=headers, json=payload)
# 	return response.json()

# def get_classification(comment: str, llm_name):
#     output = query({
#         "inputs": comment,
#         "parameters": {"candidate_labels": CANDIDATE_LABELS},
#     })
#     print(output)
    



#     # Remplacer 'your_model_name_here' par le chemin/nom de votre modèle sur Hugging Face
#     url = "https://huggingface.co/api/models/layier/unbiaised-toxic-roberta-onnx"
#     response = requests.get(url)
#     data = response.json()

#     # Afficher les fichiers disponibles
#     print(data.get('siblings', []))  # 'siblings' contient les fichiers liés au modèle

#     # get_classification("black men love pills.", model_name)