import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
import uuid
import requests
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')

openai_client = OpenAI()
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def setup_logging():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    return logging.getLogger(__name__)

async def extract_text_from_image(image_file_path):
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image? Extract all important text and give a short description of the image."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_file_path,
                        }
                    },
                ],
            }
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content

async def summarize_text(text):
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes text. Include all necessary details and make it concise."},
            {"role": "user", "content": f"Summarize the following text in short:\n\n{text}"}
        ],
        # max_tokens=200
    )
    return response.choices[0].message.content

async def generate_embedding(text):
    text = text.replace("\n", " ")
    return openai_client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

async def store_in_vector_db(embedding, text, username):
    collection_name = "user_data"
    qdrant_client.upsert(
        collection_name=collection_name,
        points=[
            {
                "id": str(uuid.uuid4()),
                "vector": embedding,
                "payload": {"text": text, "username": username}
            }
        ]
    )

async def search_vector_db(query_embedding, username):
    collection_name = "user_data"
    search_result = qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="username",
                    match=MatchValue(value=username)
                )
            ]
        ),
        limit=5
    )
    return [hit.payload['text'] for hit in search_result]

async def query_knowledge_base(query, username):
    # Generate embedding for the query
    query_embedding = await generate_embedding(query)
    
    # Search the vector database
    search_results = await search_vector_db(query_embedding, username)
    
    # Prepare the context for the LLM
    context = "\n\n".join(search_results)
    
    # Use OpenAI's LLM to generate the best response
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a powerful genius with extraordinary memory capabilities. You remember everything. You provide answers based on the memories. If the answer is not in the memory, say you don't have that information."},
            {"role": "user", "content": f"Memory:\n{context}\n\nQuestion: {query}\n\nProvide a concise and accurate answer based on the memories provided:"}
        ],
        max_tokens=150
    )
    
    return response.choices[0].message.content