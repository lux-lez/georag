import os
import mistralai

from .constants.prompts import QuestionPrompt, AnswerPrompt
from .auth import get_api_key
from .timing import timer_start, timer_end

LanguageModel = "ministral-8b-latest" 

def start_llm_client():
    llm_client = mistralai.Mistral(api_key=get_api_key("mistralai"))
    return llm_client 

def ask_llm(question : str, llm_client=None, verbose=True) -> str:
    '''
    Ask a question to an LLM
    List of available models:
    https://docs.mistral.ai/getting-started/models/models_overview/

    '''
    if llm_client is None:
        llm_client = start_llm_client()
    
    stream_response = llm_client.chat.stream(
        model = LanguageModel,
        messages = [ {"role": "user","content": question} ]
    )
    text = ""
    for chunk in stream_response:
        s = chunk.data.choices[0].delta.content
        text += s
        if verbose: print(s, end="", flush=True )
    return text

def ask_llm_with_context(question: str, context: str, llm_client=None, verbose=True) -> str:
    '''
    Ask a question to an LLM with context
    '''
    if llm_client is None:
        llm_client = start_llm_client()
    
    stream_response = llm_client.chat.stream(
        model = LanguageModel,
        messages = [
            {"role": "system", "content": AnswerPrompt.replace("CONTEXT", context)},
            {"role": "user", "content": context + "\n\n" + question}
        ]
    )
    text = ""
    for chunk in stream_response:
        s = chunk.data.choices[0].delta.content
        text += s
        if verbose: print(s, end="", flush=True )
    if verbose: print() 
    return text

def rephrase_question(query:str, llm_client=None, verbose=True) -> str:
    if llm_client is None: llm_client = start_llm_client()
    prompt = QuestionPrompt.replace("QUERY", query)
    if verbose: t = timer_start("rephrasing question")
    stream_response = llm_client.chat.complete(
        model = LanguageModel,
        messages = [ {"role": "user","content": prompt} ]
    )
    text = stream_response.choices[0].message.content
    text = text.strip()
    if verbose: timer_end(t)
    return text
