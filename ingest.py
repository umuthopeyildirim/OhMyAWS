import os
import argparse
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, GithubFileLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = "ohmyaws"
COLLECTION_NAME = "documents"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "default"
EMBEDDING_FIELD_NAME = "embedding"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
MONGODB_COLLECTION = db[COLLECTION_NAME]


def GetGithub(repo, access_token, filter_extension):
    loader = GithubFileLoader(
        repo=repo,
        access_token=access_token,
        github_api_url="https://api.github.com",
        file_filter=lambda file_path: file_path.endswith(filter_extension),
    )
    return loader


def GetPDF(url):
    loader = PyPDFLoader(url)
    return loader


def main(loader_type, **kwargs):
    if loader_type == 'github':
        loader = GetGithub(**kwargs)
    elif loader_type == 'pdf':
        loader = GetPDF(**kwargs['url'])
    else:
        raise ValueError("Unsupported loader type. Use 'github' or 'pdf'.")

    # Assuming loader has a method to fetch and return data
    data = loader.load()

    # Split docs
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=0)
    docs = text_splitter.split_documents(data)

    # Insert the documents in MongoDB Atlas Vector Search
    _ = MongoDBAtlasVectorSearch.from_documents(
        documents=docs,
        embedding=OpenAIEmbeddings(disallowed_special=()),
        collection=MONGODB_COLLECTION,
        index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Data loader selection for document ingestion.')
    parser.add_argument('--loader_type', type=str,
                        help='Type of loader to use: "github" or "pdf".')
    parser.add_argument('--repo', type=str, help='GitHub repository name.')
    parser.add_argument('--access_token', type=str,
                        help='GitHub access token.')
    parser.add_argument('--filter_extension', type=str,
                        help='File extension to filter for GitHub loader.')
    parser.add_argument('--url', type=str, help='URL for PDF loader.')

    args = parser.parse_args()

    kwargs = {k: v for k, v in vars(args).items() if v is not None}
    main(args.loader_type, **kwargs)
