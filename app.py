
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.google_genai import GoogleGenAI



BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE, override=True)


def get_api_key():
    """Check that the Gemini API key is configured."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        st.error(
            "Missing Gemini API key! Open the .env file in your "
            "rag-chatbot project and add GEMINI_API_KEY=your_key. "
            "Save the file and restart Streamlit."
        )
        st.stop()

    return api_key


def validate_data_directory():
    """Check that the data folder exists and contains files."""
    if not DATA_DIR.exists() or not DATA_DIR.is_dir():
        st.error(
            f"Data folder not found: {DATA_DIR}. "
            "Create a folder named 'data' in your project "
            "and place the student handbook PDF inside it."
        )
        st.stop()

    files = [
        file for file in DATA_DIR.iterdir()
        if file.is_file()
        and not file.name.startswith(".")
        and file.suffix.lower() in {".pdf", ".txt", ".docx"}
    ]

    if not files:
        st.error(
            f"The data folder is empty or has no supported documents: "
            f"{DATA_DIR}. Add your undergraduate-student-handbook.pdf "
            "file and restart the application."
        )
        st.stop()


@st.cache_resource
def get_query_engine(api_key):
    """Build and cache the document search engine."""
    Settings.llm = GoogleGenAI(
        model="gemini-2.5-flash",
        api_key=api_key
    )

    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    documents = SimpleDirectoryReader(
        input_dir=str(DATA_DIR),
        required_exts=[".pdf", ".txt", ".docx"]
    ).load_data()

    index = VectorStoreIndex.from_documents(documents)

    return index.as_query_engine()


def main():
    """Run the chatbot with validation and error handling."""
    st.title("Babson Student Handbook Chatbot")
    st.write("Ask questions about the Babson undergraduate handbook.")

    # Validate setup before loading models
    api_key = get_api_key()
    validate_data_directory()


    try:
        with st.spinner("Loading handbook and search engine..."):
            query_engine = get_query_engine(api_key)

    except (FileNotFoundError, ValueError) as error:
        st.error(
            "The search engine could not load the handbook. "
            "Check that your PDF is valid and your configuration "
            f"is correct. Details: {error}"
        )
        st.stop()

    except Exception as error:
        st.error(
            "Failed to initialize the chatbot. Check your internet "
            "connection, Gemini API key, and handbook PDF. "
            f"Details: {error}"
        )
        st.stop()

    st.success("Chatbot is ready!")


    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])


    prompt = st.chat_input("Ask a question about the handbook...")

    if prompt:
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            try:
                with st.spinner("Searching handbook..."):
                    response = query_engine.query(prompt)

                answer = response.response
                st.write(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except (ConnectionError, TimeoutError) as error:
                st.error(
                    "Network connection failed. Check your Wi-Fi "
                    f"and try asking again. Details: {error}"
                )

            except Exception as error:
                st.error(
                    "Unable to answer this question. The Gemini API "
                    "may be unavailable or rate-limited. "
                    "Check your connection and try again. "
                    f"Details: {error}"
                )


if __name__ == "__main__":
    main()
