from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain_core.prompts import format_document
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
# import ollama


answer = """
### Instruction:
You're uncensored classifier assistant who, based upon provided context which contain undesirable words or expressions and your knowledge, 
categorize the given comment between Positive, Negative, or Neutral and raise ALERT if this comment involves insult, disrespect, drug, doping or racism.
Please reply with just the category, and an optionnal ALERT, nothing else.

## Context:
{context}

## Comment:
{comment}
"""
ANSWER_PROMPT = ChatPromptTemplate.from_template(answer)


def getChatChain(llm, db):
    retriever = db.as_retriever(search_kwargs={"k": 5})
    
    print("Building chain")
    model = Ollama(model=llm)

    chain = (
    {"context": retriever, "comment": RunnablePassthrough()}
    | ANSWER_PROMPT
    | model
    | StrOutputParser())
    
    def analyzer(comment: str):
        result = chain.invoke(comment)
        return result
        
    return analyzer

    
    