from typing import Union, Optional, Dict, Any,List, Tuple, Optional 
from dotenv import load_dotenv
import os
import requests
from requests.auth import HTTPBasicAuth
load_dotenv()
from haystack.components.retrievers import FilterRetriever
from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore


confluence_api_token = os.getenv('CONFLUENCE_API_TOKEN')
confluence_username = os.getenv('CONFLUENCE_USERNAME')
confluence_url = os.getenv('CONFLUENCE_URL')
confluence_space_key = os.getenv('SPACE_KEY')
confluence_user_email = os.getenv('USER_EMAIL')
elasticsearch_url =os.getenv('ELASTICSEARCH_URL')
elasticsearch_username=os.getenv('ELASTICSEARCH_USERNAME')
elasticsearch_password=os.getenv("ELASTICSEARCH_PASSWORD")
elasticsearch_indexname=os.getenv("ELASTICSEARCH_INDEXNAME")


def retrieve_confluence_pages():
    """
    Retrieves and displays Confluence pages from a specified space using the Confluence REST API.

    This function uses environment variables for authentication and configuration, including
    the API token, username, URL, space key, and user email. It fetches pages from the specified
    Confluence space, extracting details such as page ID, author email, author name, account ID,
    title, and creation date. The function returns these details as lists. If any required
    environment variable is missing, or if the API request fails, an error message is printed.

    Returns:
        tuple: Lists containing page IDs, author emails, author names, account IDs, titles,
        page URLs, and creation dates.
    """
    
    if not all([confluence_api_token, confluence_username, confluence_url, confluence_space_key, confluence_user_email]):
        print("Missing one or more environment variables.")
        return

    params = {
        "spaceKey": confluence_space_key,
        "expand": "body.storage,version",
        "limit": 100,
        "start": 0,
    }

    url = f"{confluence_url}/content"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            auth=HTTPBasicAuth(confluence_user_email, confluence_api_token),
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve pages. Error: {e}")
        return

    pages = response.json().get("results", [])
    
    page_id=[] 
    email=[]
    name=[]
    accountId=[]
    title=[]
    page_url=[]
    date=[]
    for page in pages:
        
        page_id.append(page['id'])
        email.append(page['version']['by']['email'])
        name.append(page['version']['by']['publicName'])
        accountId.append(page['version']['by']['accountId'])
        title.append(page['title'])
        date.append(page['version']['friendlyWhen'])
        page_url.append(page['_links']['webui'])
        
        
    return  page_id, email,name,accountId,title,page_url,date

def extractive_generative_api(query: str) -> Optional[Dict[str, Any]]:
    """
    Sends a GET request to a local server with a query parameter and returns the JSON response if successful.

    Args:
        query (str): A string representing the query to be sent to the API.

    Returns:
        Optional[Dict[str, Any]]: A JSON object if the request is successful, None otherwise.
    """
    url = 'http://localhost/query/'
    params = {'query': query}
    headers = {'accept': 'application/json'}

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None
    
    

def query_analyzer(query: str, file_names: list[str]) -> str:
    """
    Generates a prompt for an AI assistant to classify a user query into either
    a "Retrieval" or "Summarization" category and checks for filename matches.

    :param query: A string representing the user's query.
    :param file_names: A list of strings representing filenames to check against the query.
    :return: A string prompt for an AI assistant.
    """
    file_list_str = "\n".join(f"- **{file}**" for file in file_names)

    prompt = f"""
    You are an intelligent AI assistant that classifies user queries into two categories:

    ### **1. Retrieval Query**
    Classify the query as **Retrieval** if the user is searching for specific information, facts, or details that require looking up content from a document.  
    **Example Queries:**  
    - "What is our company's vacation policy?"  
    - "Provide details about our AWS infrastructure security measures."  
    - "How does our organization handle network segmentation?"  

    ### **2. Summarization Query**
    Classify the query as **Summarization** if the user asks for a summary of a specific document, law, or policy.  
    **Example Queries:**  
    - "Summarize the contents of the DevOps Ramp-up Plan."  
    - "Give me a brief summary of the Technical Infrastructure FAQ."  
    - "What are the main points covered in the Employee Handbook?"  

    ### **Filename Matching**
    Determine if the query references a document name, even partially, from the following list:
    {file_list_str}

    A filename match should be considered **if the query directly mentions or implies content that is likely found in a specific document** (e.g., "vacation policy" relates to the Employee Handbook & Policies).  

    ### **Response Format:**
    1. Classify the query as either `"Retrieval"` or `"Summarization"`.
    2. If a filename is matched, return the filename.

    #### **Example Responses:**
    - **Retrieval only:** `"Retrieval"`
    - **Summarization only:** `"Summarization"`
    - **Summarization with filename:** `"Summarization - Employee Handbook & Policies"`
    - **Retrieval with filename:** `"Retrieval - Technical Infrastructure FAQ"`

    ---

    Now, analyze the following user query and classify it accordingly:

    **User Query:** `{query}`
    """
    return prompt


def doc_filters(file_name: Union[str, List[str]]):
    """
    Connects to an Elasticsearch document store and retrieves documents based on a filter applied to the "Page_Title" field.
    
    :param file_name: A string or a list containing a single string representing the title of the document to be retrieved.
    :return: The result of the document retrieval operation, which includes documents matching the specified "Page_Title".
    """
    document_store = ElasticsearchDocumentStore(
        hosts=elasticsearch_url,
        basic_auth=(elasticsearch_username, elasticsearch_password),
        index=elasticsearch_indexname,
        embedding_similarity_function="cosine",
        verify_certs=False,
        ca_certs=None, 
    )
    retriever = FilterRetriever(document_store)
    
    title = file_name[0] if isinstance(file_name, list) else file_name
    result = retriever.run(filters={"field": "Page_Title", "operator": "==", "value": title})
    
    return result


def summary_prompt(context: str, query: str) -> str:
    """
    Generates a structured prompt for an AI assistant to create a professional summary of given content.

    Parameters:
    context (str): The content to be summarized.
    query (str): The user's request or question related to the content.

    Returns:
    str: A formatted prompt containing instructions for generating a professional summary.
    """
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

    ** User Query**:{query}
        
    """
    return prompt

    
def concatenate_content_and_metadata(data):
    """
    Concatenates document content by their split identifiers and extracts unique metadata.

    Args:
        data (dict): A dictionary containing a list of documents under the key 'documents'.
                     Each document is expected to have 'meta' and 'content' attributes.

    Returns:
        tuple: A tuple containing:
            - str: Concatenated document content ordered by 'split_id'.
            - dict: Unique metadata extracted from the documents.
    """
    split_content = {}
    unique_metadata = {}

    for doc in data['documents']:
        split_id = doc.meta['split_id']
        content = doc.content
        if split_id not in split_content:
            split_content[split_id] = ""
        split_content[split_id] += content

        for key, value in doc.meta.items():
            if key not in unique_metadata:
                unique_metadata[key] = value

    sorted_content = {k: v for k, v in sorted(split_content.items())}
    concatenated_content = " ".join(sorted_content.values())

    return concatenated_content, unique_metadata


def check_string(input_string: str, file_names: List[str]) -> Tuple[Optional[str], List[str]]:
    """
    Check if the input string contains specific terms and which file names are mentioned.

    Args:
    - input_string (str): The string to be checked.
    - file_names (List[str]): A list of file names to check for mentions.

    Returns:
    - Tuple[Optional[str], List[str]]: A tuple containing the found term and mentioned files.
    """
    contains_term = None
    if "Retrieval" in input_string:
        contains_term = "Retrieval"
    elif "Summarization" in input_string:
        contains_term = "Summarization"
    mentioned_files = [file_name for file_name in file_names if file_name in input_string]

    return contains_term, mentioned_files


def generative(prompt: str) -> Optional[Dict[str, Any]]:
    """
    Sends a GET request to a local server to generate content based on a given prompt using a specified AI model.
    Args:
        prompt (str): The input for the content generation request.
    Returns:
        Optional[Dict[str, Any]]: The JSON response if successful, otherwise None.
    """
    
    url = 'http://localhost/generate/'
    params = {
        'prompt': prompt,
        'model': 'deepseek-ai/DeepSeek-R1'
    }
    headers = {'accept': 'application/json'}

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

def extract_text_after_tag(input_text: str, tag: str) -> str:
    """
    Extracts and returns the text following a specified HTML-like closing tag from a given input string.

    :param input_text: A string containing the text with HTML-like tags.
    :param tag: A string representing the tag name to search for in the input text.
    :return: A string containing the text after the specified closing tag, or an empty string if the tag is not found.
    """
    tag_end = f"</{tag}>"
    tag_end_index = input_text.find(tag_end)
    if tag_end_index != -1:
        return input_text[tag_end_index + len(tag_end):].strip()
    return ""