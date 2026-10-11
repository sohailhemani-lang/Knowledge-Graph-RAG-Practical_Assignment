"""
config.py — Loads environment variables for the Hybrid Graph RAG lab.
"""

import os
from dotenv import load_dotenv

# Load .env from the same directory as this file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

NEO4J_URI      = os.getenv("NEO4J_URI")
NEO4J_USER     = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.8-flash")
GEMINI_EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL",
    "gemini-embedding-001",
)

if not NEO4J_URI or not NEO4J_USER or not NEO4J_PASSWORD:
    raise EnvironmentError(
        "Neo4j connection variables (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD) "
        "are not set. Add them to your .env file."
    )

if not GEMINI_API_KEY:
    raise EnvironmentError(
        "GEMINI_API_KEY is not set. Add a valid Gemini API key to the .env file "
        "or export it as an environment variable. OpenAI API keys are not valid "
        "Gemini keys."
    )

if __name__ == "__main__":
    print("Configuration loaded:")
    print(f"  NEO4J_URI  : {NEO4J_URI}")
    print(f"  NEO4J_USER : {NEO4J_USER}")
    print("  GEMINI_KEY : configured")
