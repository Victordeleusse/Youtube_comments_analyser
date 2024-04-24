# import ollama
from scipy.spatial.distance import cosine
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings

from run_ollama_analysis import *


banned_list_dopage = "dopé, doped, Dopéd, vous êtes chargés, you're charged, stéroides, steroids, stero, roids, PED, \
use products, sous produits, utiliser des produits, utiliser des produits dopants, \
substances, fruits, bonbons, pills, testosterone, trt, TRT, hormones, testo, GH, gh, hormones, \
natural, naturel, natty"

banned_list_sex = "Pornography, Fornicate, Erotic, Intercourse, Masturbation, Orgasm, Kinky, Fetish, Vulva, Penis, \
Vagina, Ejaculation, Condom, Blowjob, Anal, Prostitute, Hooker, Escort, XXX, Adult, Swingers, Nudity, Pornographic, \
Hardcore, Sensual, Eroticize, Copulation, Sexually explicit, Sex toys, Libido, Impotence, Premature ejaculation, Prostitution, \
Erotic literature, Sexually transmitted diseases, BDSM, S&M, Threesome, Orgy, Fisting, Cunnilingus, Fellatio, Titillate, Phallic, \
Clitoris, Labia, Pubic hair, Erotic massage, Nipples, Cumbersome"


embedding_model_name = 'nomic-embed-text:latest'

def generate_banned_embeding(banned_list: str) -> dict:
    check_if_model_is_available(embedding_model_name)
    embeddings_model = OllamaEmbeddings(model=embedding_model_name)

    banned_words = banned_list.split(', ')
    banned = {
        word: embeddings_model.embed_query(word.strip())
        for word in banned_words
    }
    return banned

# def get_comment_embedded(comment: str):
#     check_if_model_is_available(embedding_model_name)
#     embeddings_model = OllamaEmbeddings(model=embedding_model_name)
#     return embeddings_model.embed_query(comment)

def generate_comment_embeding(comment: str) -> dict:
    check_if_model_is_available(embedding_model_name)
    embeddings_model = OllamaEmbeddings(model=embedding_model_name)

    comment_words = comment.split(' ')
    comment = {
        word: embeddings_model.embed_query(word.strip())
        for word in comment_words
    }
    return comment

def is_related_to_banned(comment, threshold=0.8):
    banned = generate_banned_embeding(banned_list_dopage)
    comment = generate_comment_embeding(comment)
    
    for word_c, emb_c in comment.items():
        for word_banned, emb_banned in banned.items():
            similarity = 1 - cosine(emb_banned, emb_c)
            if similarity > threshold:
                print("banned word found", similarity, word_c)
                return True, word_c
    return False, None

comment = "Stop takink bonbon !"

if __name__ == "__main__":
    is_it, word = is_related_to_banned(comment)
    print(word)
    



    
    