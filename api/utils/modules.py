from haystack.utils import ComponentDevice
from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore
from haystack_integrations.components.retrievers.elasticsearch import (
    ElasticsearchEmbeddingRetriever,
    ElasticsearchBM25Retriever
)
from haystack.components.embedders import SentenceTransformersTextEmbedder
import requests
import time
from haystack.components.joiners import DocumentJoiner
from haystack.components.rankers import TransformersSimilarityRanker
from haystack import Pipeline
from dotenv import load_dotenv
import os
from pathlib import Path
env_path = Path(__file__).resolve().parents[2] / ".env"  # Navigate up to project root
load_dotenv(dotenv_path=env_path)


# Load API Token
api_token = os.getenv("TOGETHER_TOKEN")
elasticsearch_url =os.getenv('ELASTICSEARCH_URL')
elasticsearch_username=os.getenv('ELASTICSEARCH_USERNAME')
elasticsearch_password=os.getenv("ELASTICSEARCH_PASSWORD")
elasticsearch_indexname=os.getenv("ELASTICSEARCH_INDEXNAME")



def summary_prompt(context):
    prompt=f""" 
    You are an expert AI assistant specializing in fact-based, structured, and professional summarization. Your task is to generate a concise yet detailed summary of the provided content while maintaining its original intent, technical accuracy, and key takeaways.

**Instructions**:
    Summarize the given content professionally by following these key principles:

1. Concise Yet Comprehensive:

    - Capture all essential information without losing depth.
    - Avoid unnecessary repetition or verbose explanations.
2.  **Well-Structured Format**:

    - Use clear headings, bullet points, or sections to improve readability.
    - If the content includes tables, code snippets, JSON structures, or SQL queries, ensure their integrity.

3. **Context & Relation Preservation**:

    - Maintain relationships between concepts, hierarchical data, and technical components.
    - If summarizing legal, academic, or technical documents, retain accuracy and key terminology.

4. **Technical Depth (if applicable)**:

    - If the content is technical, explain key concepts, best practices, and relevant optimizations.
    - Use examples when necessary but avoid unnecessary elaboration.

5. **Professional & Neutral Tone**:

    - Use formal and authoritative language.
    - Avoid assumptions or adding external information.
6. **Handling Unclear or Insufficient Information**:

    - If the provided content lacks enough details, clearly state:
    - "The given content does not provide sufficient details for a comprehensive summary."
    - Do not attempt to fabricate missing information.
    
**Input Content**:{context}
    
**Output Summary:**
    """
    return prompt


# Generative function with retry logic
def generative(prompt: str, model="deepseek-ai/DeepSeek-R1") -> str:
    """
    Generates a response using the Together API with retry logic.

    Args:
        prompt (str): The input prompt.
        model (str): The model to use (default: "deepseek-ai/DeepSeek-R1").

    Returns:
        str: The model's response.
    """
    HEADERS = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json",
    }
    timeout = 60
    retry_count = 3
    backoff_time = 10  # Time to wait before retrying

    url = "https://api.together.xyz/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": None,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "stop": ["<｜end▁of▁sentence｜>"],
    }

    for attempt in range(retry_count):
        try:
            response = requests.post(url, headers=HEADERS, json=payload, timeout=timeout)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.RequestException as e:
            print(f"Attempt {attempt+1} failed: {e}")

            if attempt < retry_count - 1:
                print(f"Retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)
            else:
                print("Max retries reached. Returning None.")

    return None
# Prompting function
def prompting(user_query, context):
    prompt = f"""
    ### System Role:
    You are an AI assistant trained to provide fact-based, precise, and well-structured answers based on retrieved documents. 
    Use the provided context, metadata, and user query to generate a high-quality response. If the provided information is insufficient, 
    respond with: "The given context does not contain enough details to answer this query."

    ### Context:
    {context}  

    ### User Query:
    {user_query}  

    ### Response Guidelines:
    - **Accuracy & Relevance**: Extract and summarize relevant information strictly from the provided context.  
    - **Data Structure Awareness**: If the context includes SQL queries, hierarchical data, JSON structures, or tabular data, 
      maintain their integrity in the response.  
    - **Technical Depth**: If the query is technical, provide optimizations, best practices, or alternative solutions.  
    - **Context Preservation**: Ensure that the response preserves relationships between data elements.  
    - **Clarity & Readability**: Structure responses clearly with bullet points, explanations, and code formatting (if applicable).  
    - **Uncertainty Handling**: If the context lacks enough information, state:  
      _"The provided context does not contain sufficient details to answer this question."_  

    """
    return prompt

# Elasticsearch Document Store
document_store = ElasticsearchDocumentStore(
        hosts=elasticsearch_url,
        basic_auth=(elasticsearch_username, elasticsearch_password),
        index=elasticsearch_indexname,
        embedding_similarity_function="cosine",
        verify_certs=False,
        ca_certs=None, 
    )

# Embedding Retriever and BM25 Retriever
embedding_retriever = ElasticsearchEmbeddingRetriever(document_store=document_store, top_k=3, num_candidates=3)
embadder = SentenceTransformersTextEmbedder(model="BAAI/bge-m3", device=ComponentDevice.from_str("cuda:0"))
bm25_retriever = ElasticsearchBM25Retriever(document_store=document_store, top_k=3)

# Joiner & Ranker
document_joiner = DocumentJoiner()
ranker = TransformersSimilarityRanker(model="BAAI/bge-reranker-base", top_k=1, device=ComponentDevice.from_str("cuda:0"))

# Hybrid Retrieval Pipeline
hybrid_retrieval = Pipeline()
hybrid_retrieval.add_component("text_embedder", embadder)
hybrid_retrieval.add_component("embedding_retriever", embedding_retriever)
hybrid_retrieval.add_component("bm25_retriever", bm25_retriever)
hybrid_retrieval.add_component("document_joiner", document_joiner)
hybrid_retrieval.add_component("ranker", ranker)

hybrid_retrieval.connect("text_embedder", "embedding_retriever")
hybrid_retrieval.connect("bm25_retriever", "document_joiner")
hybrid_retrieval.connect("embedding_retriever", "document_joiner")
hybrid_retrieval.connect("document_joiner", "ranker")


# Query Endpoint
async def query_endpoint(query: str):
    """
    Handles the query endpoint logic.

    Args:
        query (str): The input query.

    Returns:
        dict: The responses and metadata generated by the query endpoint.
    """
    result = hybrid_retrieval.run(
        {
            "text_embedder": {"text": query},
            "bm25_retriever": {"query": query},
            "ranker": {"query": query}
        }
    )

    responses = []
    for doc in result.get('ranker', {}).get('documents', []):
        # Generate the prompt result using the query and document content
        prompt_result = prompting(query, doc.content)
        
        # Generate the response using the prompt result
        generative_response = generative(prompt_result)
        
        # Extract metadata
        metadata = {
            "Page_Title": doc.meta.get('Page_Title', 'Unknown'),
            "Author_Name": doc.meta.get('Author_Name', 'Unknown'),
            "Date": doc.meta.get('Date', 'Unknown'),
            "Page_URL": doc.meta.get('Page_URL', 'Unknown'),
            "Author_Email": doc.meta.get('Author_Email', 'Unknown')
        }
        
        # Append the response and metadata to the responses list
        responses.append({
            "response": generative_response,
            "metadata": metadata
        })

    return {"responses": responses}