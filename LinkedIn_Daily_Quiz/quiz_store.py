import os
import json
from azure.storage.blob import BlobServiceClient

CONN_ENV = "STORAGE_CONNECTION_STRING"

def _blob_client(container, blob):
    """
        Create and return a client object for a specific blob file in Azure Storage.
        Looks up the storage connection string from the environment variable
        STORAGE_CONNECTION_STRING. If the variable is missing, it raises an error.
    """
    conn = os.environ.get(CONN_ENV)
    if not conn:
        raise RuntimeError(f"{CONN_ENV} not set")
    svc = BlobServiceClient.from_connection_string(conn)
    return svc.get_blob_client(container=container, blob=blob)

def load_questions(container, blob):
    """
        Load the quiz questions from a JSON file stored in an Azure Blob.
        - If the blob exists and contains valid JSON, return its contents as a Python list.
        - If the blob is missing or unreadable, return an empty list instead.
    """
    bc = _blob_client(container, blob)
    try:
        data = bc.download_blob().readall()
        return json.loads(data)
    except Exception:
        return []

def save_questions(container, blob, items):
    """
        Save the given list of quiz questions to the blob file in Azure Storage.
        - The existing blob will be overwritten with the new JSON data.
        - The JSON is written with indentation and keeps non-ASCII characters.
    """
    bc = _blob_client(container, blob)
    text = json.dumps(items, indent=2, ensure_ascii=False)
    bc.upload_blob(text, overwrite=True)

def append_question(container, blob, item):
    """
        Add one new quiz question to the end of the list in the blob file.
        - Reads the current list of questions from the blob (or uses an empty list if none).
        - Appends the new question dictionary.
        - Saves the updated list back to the blob.
        - Returns the full updated list of questions.
    """
    items = load_questions(container, blob)
    items.append(item)
    save_questions(container, blob, items)
    return items