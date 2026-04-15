"""
Read txt files from a document folder, generate embeddings using SLM API,
store them in InMemoryVectorStore via add_documents,
save all texts with embeddings into JSON file.

How to run:
python -m app.data.data_embedding
"""

import os
import json
import uuid
from pathlib import Path
from typing import List, Dict, Optional

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document

from app.core.config import slm_embedding

_VECTORSTORE: Optional[InMemoryVectorStore] = None


def build_vectorstore_and_save_json(
        input_directory: str,
        output_file: str,
) -> InMemoryVectorStore:
    """
    1. Read all .txt files from input_directory
    2. Generate embeddings using SLM API
    3. Save all texts + embeddings + metadata into a single JSON file
    4. Build an InMemoryVectorStore by adding Document objs
    args:
        input_directory (str): Directory containing .txt files
        output_file (str): Path to save the JSON file with embeddings
    returns:
        InMemoryVectorStore: The built vectorstore with documents added
    """
    json_records: List[Dict] = []
    documents: List[Document] = []

    if not os.path.exists(input_directory):
        raise FileNotFoundError(f"input_directory not found: {input_directory}")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    for filename in os.listdir(input_directory):
        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(input_directory, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        record_id = str(uuid.uuid4())

        # Generate embedding using SLM API
        embedding = slm_embedding.embed_query(text)

        json_records.append(
            {
                "id": record_id,
                "filename": filename,
                "content": text,
                "embedding": embedding,
            }
        )

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "id": record_id,
                    "filename": filename,
                },
            )
        )

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(json_records, f, indent=4, ensure_ascii=False)

    # Build InMemoryVectorStore
    vectorstore = InMemoryVectorStore(slm_embedding)
    vectorstore.add_documents(documents)

    return vectorstore


def get_vectorstore() -> InMemoryVectorStore:
    """
    Lazily initialize and return the in-memory vectorstore.

    IMPORTANT:
    - This makes `from app.data.data_embedding import get_vectorstore` safe.
    - Avoids building vectorstore at import time.
    """
    global _VECTORSTORE

    if _VECTORSTORE is None:
        script_dir = Path(__file__).parent
        input_directory = script_dir / "document"
        output_file = script_dir / "embeddings" / "all_text_embeddings.json"

        _VECTORSTORE = build_vectorstore_and_save_json(
            input_directory=str(input_directory),
            output_file=str(output_file),
        )

    return _VECTORSTORE


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    output_file = script_dir / "embeddings" / "all_text_embeddings.json"
    print("VectorStore created and embeddings saved to:", str(output_file))
