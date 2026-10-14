"""
config.py — Loads environment variables for the Hybrid Graph RAG lab.
"""

import os
from dotenv import load_dotenv
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

# Load .env from the same directory as this file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


def _get_setting(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value:
        return value

    try:
        return st.secrets.get(name, default)
    except StreamlitSecretNotFoundError:
        return default


NEO4J_URI = _get_setting("NEO4J_URI")
NEO4J_USER = _get_setting("NEO4J_USER")
NEO4J_PASSWORD = _get_setting("NEO4J_PASSWORD")
OPENAI_API_KEY = _get_setting("OPENAI_API_KEY")
OPENAI_CHAT_MODEL = _get_setting("OPENAI_CHAT_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = _get_setting(
    "OPENAI_EMBEDDING_MODEL",
    "text-embedding-3-small",
)

if not NEO4J_URI or not NEO4J_USER or not NEO4J_PASSWORD:
    raise EnvironmentError(
        "Neo4j connection variables (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD) "
        "are not set. Add them to your .env file or Streamlit Cloud Secrets."
    )

if not OPENAI_API_KEY:
    raise EnvironmentError(
        "OPENAI_API_KEY is not set. Add a valid OpenAI API key to the .env file, "
        "Streamlit Cloud Secrets, or the environment."
    )

if __name__ == "__main__":
    print("Configuration loaded:")
    print(f"  NEO4J_URI  : {NEO4J_URI}")
    print(f"  NEO4J_USER : {NEO4J_USER}")
    print("  OPENAI_KEY : configured")
