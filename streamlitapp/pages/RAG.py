import sys
import os
import streamlit as st
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from streamlitapp.utils import extractive_generative_api, extract_text_after_tag,retrieve_confluence_pages,query_analyzer,generative,check_string,doc_filters,concatenate_content_and_metadata,summary_prompt


st.set_page_config(page_title="RAG", page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)


page_id, email, name, accountId, title, page_url,date = retrieve_confluence_pages()
page_data = [page_id, title,email, name, accountId, page_url,date]
pages_list_data = [lst[1:] for lst in page_data]
filenames=pages_list_data[1]

def retrival_func(query: str) -> str:
    """
    Sends a query to an API and extracts text following the 'think' tag from the response.

    Args:
        query (str): The query to be sent to the API.

    Returns:
        str: The text extracted after the 'think' tag from the API response.
    """
    response = extractive_generative_api(query)
    for response in response["responses"]:
        text = response["response"]
        meta_data=response["metadata"]
    refine_response = extract_text_after_tag(text, 'think')
    return refine_response,meta_data

prompt = st.chat_input("Say something")
if prompt:
    query_analyzer_prompt=query_analyzer(prompt,filenames) 
    response_query_analyzer=generative(query_analyzer_prompt)   
    refine_response=extract_text_after_tag(response_query_analyzer,'think')
    type,which_file=check_string(refine_response,filenames)
    
    if type=='Retrieval':
        retrive_text,meta_data=retrival_func(prompt)
        
        with st.chat_message("user"):
            st.write(f"{prompt}")
        
        message = st.chat_message("assistant")
        message.write(f"{retrive_text}")
        message.markdown("### 📄 **Confluence Page Metadata**")
        message.markdown(f"**📌 Title:** {meta_data['Page_Title']}")
        message.markdown(f"**👤 Author:** {meta_data['Author_Name']}")
        message.markdown(f"**📅 Date:** {meta_data['Date']}")
        message.markdown(f"**📧 Contact:** [{meta_data['Author_Email']}](mailto:{meta_data['Author_Email']})")
        
    elif type=='Summarization' and which_file is not None :
        
        filter_data=doc_filters(which_file)
        
        complete_context,meta_data=concatenate_content_and_metadata(filter_data)
        response=generative(summary_prompt(complete_context,prompt))
        final_answer=extract_text_after_tag(response,'think')
        with st.chat_message("user"):
            st.write(f"{prompt}")
        message = st.chat_message("assistant")
        message.write(f"{final_answer}")
        message.markdown("### 📄 **Confluence Page Metadata**")
        message.markdown(f"**📌 Title:** {meta_data['Page_Title']}")
        message.markdown(f"**👤 Author:** {meta_data['Author_Name']}")
        message.markdown(f"**📅 Date:** {meta_data['Date']}")
        message.markdown(f"**📧 Contact:** [{meta_data['Author_Email']}](mailto:{meta_data['Author_Email']})")
        
    else:
        
        retrive_text,meta_data=retrival_func(prompt)
        with st.chat_message("user"):
            st.write(f"{prompt}")
        
        message = st.chat_message("assistant")
        message.write(f"{retrive_text}")
        message.markdown("### 📄 **Confluence Page Metadata**")
        message.markdown(f"**📌 Title:** {meta_data['Page_Title']}")
        message.markdown(f"**👤 Author:** {meta_data['Author_Name']}")
        message.markdown(f"**📅 Date:** {meta_data['Date']}")
        message.markdown(f"**📧 Contact:** [{meta_data['Author_Email']}](mailto:{meta_data['Author_Email']})")