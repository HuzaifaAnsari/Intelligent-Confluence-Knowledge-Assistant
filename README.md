# Intelligent Confluence Knowledge Assistant

The **Intelligent Confluence Knowledge Assistant** is an advanced system designed to facilitate seamless querying of company documentation within Confluence. The assistant integrates a **Retrieval-Augmented Generation (RAG)** system, enabling users to retrieve and generate accurate responses from Confluence content using natural language queries.

## Features
- **RAG-Based Querying:** Retrieve relevant information from Confluence using advanced retrieval techniques.
- **Elasticsearch Integration:** Store and search indexed Confluence content efficiently.
- **FastAPI Backend:** API-based architecture for seamless integration.
- **Streamlit UI:** User-friendly interface for querying documents.
- **Together.AI Support:** Leverage AI-powered LLMs for enhanced search performance.

## Installation Guide

### Clone the Repository
```bash
git clone https://github.com/HuzaifaAnsari/Intelligent-Confluence-Knowledge-Assistant.git
cd Intelligent-Confluence-Knowledge-Assistant
```

### Install Elasticsearch using Docker

1. **Install Docker:** Follow the official Docker installation guide for your system: [Get Docker](https://docs.docker.com/get-started/get-docker/).

   - If using Docker Desktop, allocate at least **4GB of memory** in `Settings > Resources`.

2. **Create a Docker network for Elasticsearch:**
```bash
docker network create elastic
```

3. **Pull the Elasticsearch Docker image:**
```bash
docker pull docker.elastic.co/elasticsearch/elasticsearch:8.17.2
```

4. **Start an Elasticsearch container:**
```bash
docker run --restart always --name es01 --net elastic -p 9200:9200 -it -m 6GB \
-e "xpack.ml.use_auto_machine_memory_percent=true" \
docker.elastic.co/elasticsearch/elasticsearch:8.17.2
```
   - The command will print the **Elasticsearch user password** and an **enrollment token**.
   - Copy the **username** and **password**, and paste them into the `.env` file.

### Configure Environment Variables
Update the `.env` file with the required credentials:
- **Elasticsearch Credentials** (username & password from Elasticsearch setup)
- **Confluence API Credentials**
  - `CONFLUENCE_API_TOKEN`
  - `CONFLUENCE_USERNAME`
  - `CONFLUENCE_EMAIL`
  - `CONFLUENCE_SPACE_KEY`
- **Together.AI API Key** (Sign up at [Together.AI](https://www.together.ai/) and store the key in `.env`)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Store Embeddings into Elasticsearch
Run the embedding script to index Confluence data into Elasticsearch.
```bash
python embedding.py
```

### Start the FastAPI Backend
```bash
uvicorn main:app --host 0.0.0.0 --port 80
```

### Start the Streamlit Application
```bash
streamlit run Home.py
```

## Usage
1. Access the **Streamlit UI** to enter your query and retrieve information from Confluence.
2. The **FastAPI backend** processes the query using the RAG system and fetches the relevant information.
3. Elasticsearch indexes and retrieves relevant content efficiently.


## Contributions
Contributions are welcome! Feel free to submit a pull request or open an issue.

## Contact
For questions or support, reach out to [Email](huzaifamuqeem@gmail.com) or [GitHub profile](https://github.com/HuzaifaAnsari).

