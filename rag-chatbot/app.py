import os

import streamlit as st
from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.google_genai import GoogleGenAI

load_dotenv()

DATA_DIR = "data"

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY not found. Check your .env file.")
    st.stop()

Settings.llm = GoogleGenAI(
    model="gemini-2.5-flash",
    api_key=api_key
)

Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)


def get_query_engine():
    """Load the handbook, create an index, and return a query engine."""


    if not os.getenv("GEMINI_API_KEY"):
        st.error("GEMINI_API_KEY not found. Add it to your .env file.")
        st.stop()


    documents = SimpleDirectoryReader(DATA_DIR).load_data()


    index = VectorStoreIndex.from_documents(documents)


    return index.as_query_engine()



st.title("Babson Student Handbook Chatbot")


if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


prompt = st.chat_input("Ask a question about the Babson student handbook")


if prompt:


    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )


    with st.chat_message("user"):
        st.write(prompt)


    query_engine = get_query_engine()


    response = query_engine.query(prompt)


    answer = response.response


    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )


    with st.chat_message("assistant"):
        st.write(answer)

