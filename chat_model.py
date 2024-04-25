# import ollama
from scipy.spatial.distance import cosine
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings

from run_ollama_analysis import *
# from utils import *



# model_name = os.getenv("BASE_LLM_MODEL")
model_name = 'mistral:latest'
# embedding_model_name = os.getenv("BASE_EMBEDDING_MODEL")
embedding_model_name = 'nomic-embed-text:latest'


def generate_banned_embeding(banned_list: str) -> dict:
    # check_if_model_is_available(embedding_model_name)
    embeddings_model = OllamaEmbeddings(model=embedding_model_name)

    banned_words = banned_list.split(', ')
    banned = {
        word: embeddings_model.embed_query(word.strip())
        for word in banned_words
    }
    return banned

BANNED_LIST_DOPAGE = os.getenv("BANNED_LIST_DOPAGE")
banned_dict_dopage = generate_banned_embeding(BANNED_LIST_DOPAGE)
BANNED_LIST_SEX = os.getenv("BANNED_LIST_SEX")
banned_dict_sex = generate_banned_embeding(BANNED_LIST_SEX)
BANNED_LIST_RACISM = os.getenv("BANNED_LIST_RACISM")
banned_dict_racism = generate_banned_embeding(BANNED_LIST_RACISM)
banned_dict_lst = [banned_dict_dopage, banned_dict_sex, banned_dict_racism]

# def get_comment_embedded(comment: str):
#     check_if_model_is_available(embedding_model_name)
#     embeddings_model = OllamaEmbeddings(model=embedding_model_name)
#     return embeddings_model.embed_query(comment)

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
    # print(f"Translated message : {full_translated_msg}")
    return full_translated_msg.lower()

def generate_comment_embeding(comment: str) -> dict:
    # check_if_model_is_available(embedding_model_name)
    embeddings_model = OllamaEmbeddings(model=embedding_model_name)
    translated_comment = comment_translator(comment, model_name)
    print(translated_comment)
    translated_comment_words = translated_comment.split(' ')
    comment = {
        word: embeddings_model.embed_query(word.strip())
        for word in translated_comment_words
    }
    return comment


def is_related_to_banned(banned_list: list, comment:str, threshold=0.9):
    comment = generate_comment_embeding(comment)
    
    for banned in banned_list:
        for word_com, emb_comm in comment.items():
            for word_banned, emb_banned in banned.items():
                print(f"{word_com} vs. {word_banned}")
                similarity = 1 - cosine(emb_banned, emb_comm)
                if similarity > threshold:
                    print("banned word found", similarity, word_com)
                    return True, word_com
    return False, None

comment1 = "Incredible the video! However, in my opinion, he is no longer the best French bodybuilder. He has been surpassed by Stéphane Matala. Despite not being the same category."
comment2 = "Dopéd vs naturel: it was necessary to specify in the title."

if __name__ == "__main__":
    is_it, word = is_related_to_banned(banned_dict_lst, comment2)
    print(word)
    



    
    