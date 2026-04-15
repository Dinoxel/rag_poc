'''
language models configuration for embedding and text generation
Import this module to access the configured models.
'''

import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

load_dotenv()

API_KEY = os.getenv("API_KEY")

slm_embedding = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=API_KEY
)

llm_generation = ChatOpenAI(
    model="gpt-5.2-2025-12-11",
    api_key=API_KEY
)
