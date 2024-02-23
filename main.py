import argparse
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
from langchain_openai import OpenAIEmbeddings, ChatOpenAI


# Load environment variables
load_dotenv()

# Database configuration
MONGO_URI = os.getenv('MONGO_URI')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not MONGO_URI or not OPENAI_API_KEY:
    raise Exception(
        "Missing required environment variables: `MONGO_URI` and/or `OPENAI_API_KEY`.")

DB_NAME = "ohmyaws"
COLLECTION_NAME = "documents"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "default"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
MONGODB_COLLECTION = db[COLLECTION_NAME]

# Setup for context retrieval and response generation
vectorstore = MongoDBAtlasVectorSearch.from_connection_string(
    MONGO_URI,
    f"{DB_NAME}.{COLLECTION_NAME}",
    OpenAIEmbeddings(disallowed_special=(), api_key=OPENAI_API_KEY),
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
)
retriever = vectorstore.as_retriever()

# RAG prompt
template = """Answer the question based only on the following context:
{context}
Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

# Setup OpenAI Chat model
model = ChatOpenAI(api_key=OPENAI_API_KEY)

chain = (
    RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
    | prompt
    | model
    | StrOutputParser()
)


def ask_question(question_str: str):
    # Assuming there's an `execute` method or similar
    # Replace `run` with the correct method
    result = chain.invoke(question_str)
    print("Response:", result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ask a question and get a response with context search on MongoDB.")
    parser.add_argument("question", type=str, help="The question to ask.")

    args = parser.parse_args()

    ask_question(args.question)
