import os
import meilisearch
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()
MEILISEARCH_API_KEY = os.environ["MAPIKEY"]
client = meilisearch.Client("http://127.0.0.1:7700", MEILISEARCH_API_KEY)
index = client.index("logs")


def add_log(log):
    index.add_documents([{"id": str(uuid4()), **log}])


def search_logs(query):
    result = index.search(query)
    return result
