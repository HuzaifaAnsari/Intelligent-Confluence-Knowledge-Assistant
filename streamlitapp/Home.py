import streamlit as st


# Setup the Streamlit layout
st.set_page_config(page_title="Intelligent Confluence Knowledge Assistant", layout="wide")
st.title("Intelligent Confluence Knowledge Assistant")
st.header("Introduction")

intro="""
The Intelligent Confluence Knowledge Assistant is a state-of-the-art AI-powered system designed to enhance document accessibility and knowledge discovery within an organization. It enables users to query company documentation using natural language, allowing for a seamless and intuitive interaction with vast amounts of corporate knowledge stored in Atlassian Confluence.

By leveraging Retrieval-Augmented Generation (RAG), the system ensures accurate, contextually relevant, and up-to-date responses based on the company’s internal documentation. Additionally, it provides users with the flexibility to select specific documents for summarization, enabling efficient knowledge extraction tailored to their needs.
"""
st.markdown(intro)
st.divider()

st.header("Key Features")
st.subheader("1. Natural Language Querying")
st.markdown("""- Users can interact with company documentation using conversational queries, eliminating the need for complex keyword searches.
- The system understands context, intent, and domain-specific terminology, ensuring precise responses.
""")
st.subheader("2. Advanced Retrieval-Augmented Generation (RAG) Architecture")

st.markdown(""" 
            - Combines retrieval-based search with generative AI capabilities to deliver fact-based, high-quality answers.
- Ensures responses are derived exclusively from Confluence content, maintaining accuracy and reliability.
            """)


st.subheader("3. Document-Specific Summarization")
st.markdown("""
            -   Users can select specific documents for summarization, allowing for quick insights without manually reviewing lengthy reports.
-   The summarization process maintains the structural integrity of tables, code snippets, and hierarchical data to preserve meaning.
            """)
st.subheader("4. Intelligent Ranking & Relevance Filtering ")
st.markdown("""
            -   Implements semantic search and re-ranking to prioritize the most relevant document sections.
-   Uses advanced vector embeddings and similarity scoring to refine search accuracy.
            
            """)

st.divider()
st.header("How It Works")
st.subheader("1. User Query Submission")
st.markdown("""
            -   A user submits a question in natural language (e.g., "What are the security protocols for cloud deployments?").
            """)
st.subheader("2. Document Retrieval & Ranking")
st.markdown("""
            
            -   The system searches Confluence using BM25 retrieval and dense vector embeddings to identify relevant content.
-   A reranker model further refines the search results based on relevance.
            """)

st.subheader("3. Context-Based Response Generation (RAG)")
st.markdown("""
            -   The most relevant document sections are fed into the LLM, which generates a coherent, structured, and factually grounded response.
            """)
st.subheader("4. Summarization Option")
st.markdown("""
            -   If the user requests a summary, the system processes the selected document and generates a concise yet comprehensive summary while preserving key information.
            """)
st.subheader("5. Response Delivery")
st.markdown("""
            -   The final answer or summary is presented to the user in a professional, well-structured format, including references to the original documentation.
            """)
st.divider()
st.header("Business Impact & Benefits")
st.markdown("""
            -   Enhanced Productivity: Employees can quickly retrieve critical information without manually searching through extensive documentation.
-   Improved Decision-Making: Fact-based, AI-assisted responses help teams make informed business decisions.
-   Reduced Time Spent on Knowledge Discovery: The system eliminates the inefficiencies of traditional keyword-based searches.
-   Scalability & Adaptability: Designed to handle large-scale corporate knowledge bases, ensuring continuous improvement through machine learning.
            """)