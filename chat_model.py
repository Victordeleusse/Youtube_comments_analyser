from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain_core.prompts import format_document
from langchain.chains import RetrievalQA

answer = """
### Instruction:
You're uncensored classifier assistant who, based upon provided context which contain undesirable words or expressions and your knowledge, 
categorize comment between Positive, Negative, or Neutral and raise ALERT if this comment involves insult, disrespect, drug, doping or racism.
Please reply with just the category, and an optionnal ALERT, nothing else.

## Context:
{context}

## Comment:
{comment}
"""
ANSWER_PROMPT = ChatPromptTemplate.from_template(answer)


def getChatChain(llm, db):
    # retriever = db.as_retriever(search_kwargs={"k": 10})
    retriever = db
    qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=retriever,
    chain_type_kwargs={"prompt": ANSWER_PROMPT})
    
    def analyzer(comment: str):
        inputs = {"comment": comment}
        result = qa_chain.invoke(inputs)
        
    return analyzer

    
    