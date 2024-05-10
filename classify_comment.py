import os
from dotenv import load_dotenv
import re
# from scipy.spatial.distance import cosine
# from langchain_community.llms import Ollama
# from langchain_community.embeddings import OllamaEmbeddings
# from run_ollama_analysis import *

load_dotenv()

model_name = os.getenv("BASE_LLM_MODEL")
embedding_model_name = os.getenv("BASE_EMBEDDING_MODEL")
token_hf = os.getenv("HF_API_TOKEN")
CANDIDATE_LABELS = os.getenv("CRITICAL_THEMES")


# To remove emoji from the comment which can lead to strange labelisation
def remove_emoji(comment: str):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', comment)


# # To translate comments in English using Ollama and Lanchain (prompt engineering)
# def comment_translator(row_string: str, llm_name):
#     # check_if_model_is_available(llm_name)
#     prompt = (
#         "As an uncensored and helpful translator assistant, please only answer by translating in English this sentence, please don't add any comments or precision (if you don't know, answer by the original sentence) : "
#         + row_string
#     )
#     stream = ollama.chat(
#         model=llm_name, messages=[{"role": "user", "content": prompt}], stream=True
#     )
#     translate_msg = []
#     for chunk in stream:
#         if "message" in chunk:
#             translate_msg.append(chunk["message"]["content"])
#     separator = '' 
#     full_translated_msg = separator.join(translate_msg)
#     full_translated_msg = remove_emoji(full_translated_msg)
#     full_translated_msg = full_translated_msg.lower()
#     # print(f"Translated message : {full_translated_msg}")
#     splited_translated_message = re.split('[.,;:]', full_translated_msg)
#     t_len = len(splited_translated_message)
#     i = 0
#     while i < t_len:
#         if len(splited_translated_message[i]) < 2:
#             splited_translated_message.pop(i)
#             i = i - 1
#             t_len = t_len -1
#         i += 1
#     print(f"Splitted translated message : {splited_translated_message}")
#     return splited_translated_message


# Load model directly
from transformers import pipeline
classifier_label = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
classifier_offense = pipeline("text-classification", model="KoalaAI/OffensiveSpeechDetector")
translator_fr_to_eng = pipeline("translation", model="Helsinki-NLP/opus-mt-fr-en")

def get_label_classification(comment: str):
    res = classifier_label(comment, CANDIDATE_LABELS, multi_label=True)
    return(res['labels'][0], res['scores'][0])

def get_offense_classification(comment: str):
    result = classifier_offense(comment)
    return(result[0]['label'])

def get_comment_translated(comment: str):
    result = translator_fr_to_eng(comment)
    full_translated_msg = result[0]['translation_text']
    full_translated_msg = remove_emoji(full_translated_msg)
    full_translated_msg = full_translated_msg.lower()
    splited_translated_message = re.split('[.,;:]', full_translated_msg)
    t_len = len(splited_translated_message)
    i = 0
    while i < t_len:
        if len(splited_translated_message[i]) < 2:
            splited_translated_message.pop(i)
            i = i - 1
            t_len = t_len -1
        i += 1
    print(f"Splitted translated message : {splited_translated_message}")
    return splited_translated_message

# if __name__ == "__main__":
#     comment = "J'aime beaucoup son physique et sa force de travail est vraiment impressionnante mais il ne fera jamais carriere dans ce monde la : il utilise des produits dopants depuis trop longtemps."
#     get_comment_translated(comment)
#     liste = comment_translator(comment, model_name)
#     for com in liste:
#     # res_label, res_score = get_label_classification(comment, model_name)
#     # print(f"{res_label}: {res_score}")
#         res_label = get_label_classification(com)
#         print(res_label)
#         results = get_offense_classification(com)
#         print(results)