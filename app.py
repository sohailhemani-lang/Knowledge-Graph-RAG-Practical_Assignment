"""Streamlit interface for the Hybrid Knowledge Graph RAG movie assistant."""

from __future__ import annotations

import time

import httpx
import streamlit as st
from openai import OpenAIError
from neo4j.exceptions import Neo4jError

from error_messages import openai_error_message

st.set_page_config(
    page_title="Hybrid Movie Assistant",
    page_icon="🎬",
    layout="centered",
)

st.title("🎬 Hybrid Knowledge Graph RAG Movie Assistant")
st.caption(
    "Ask about movie relationships or get recommendations grounded in the movie dataset."
)
st.markdown(
    "Relationship questions use the **Neo4j knowledge graph**; "
    "descriptive and recommendation questions use **FAISS vector search**."
)

SAMPLE_QUESTIONS = [
    "Who acted in The Matrix?",
    "Who directed Inception?",
    "Which actors have worked with Tom Hanks?",
    "Recommend a film about dreams or alternate realities.",
    "Find a science-fiction movie with a mind-bending story.",
    "Who directed Avatar?",
]


def _method_label(retriever: str) -> str:
    labels = {
        "graph": "Knowledge Graph (Neo4j)",
        "vector": "Vector Search (FAISS)",
        "hybrid": "Hybrid (Neo4j + FAISS)",
    }
    return labels.get(retriever, "Unknown retrieval method")


def _render_message(message: dict) -> None:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and not message.get("error"):
            st.caption(
                f"Retrieval: {_method_label(message['retriever'])} "
                f"· Response time: {message['elapsed']:.2f}s"
            )
            context = message.get("context", "").strip()
            if context:
                with st.expander("Retrieved context"):
                    st.text(context)


with st.sidebar:
    st.subheader("Try a question")
    for question in SAMPLE_QUESTIONS:
        st.markdown(f"- {question}")
    st.divider()
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.caption(
        "Configure Neo4j and OpenAI in a local .env file or Streamlit Cloud Secrets."
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

for chat_message in st.session_state.messages:
    _render_message(chat_message)

prompt = st.chat_input("Ask about a movie, actor, director, or recommendation")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    _render_message(st.session_state.messages[-1])

    started_at = time.perf_counter()
    try:
        from rag_chain import run_hybrid_rag

        with st.spinner("Searching the movie graph and knowledge base..."):
            result = run_hybrid_rag(prompt, verbose=False)
        response = {
            "role": "assistant",
            "content": result["answer"],
            "retriever": result["retriever"],
            "context": result["context"],
            "elapsed": time.perf_counter() - started_at,
        }
    except OSError:
        response = {
            "role": "assistant",
            "content": (
                "Configuration is incomplete. Check that your local `.env` file "
                "or Streamlit Cloud Secrets contain `NEO4J_URI`, `NEO4J_USER`, "
                "`NEO4J_PASSWORD`, and `OPENAI_API_KEY` with a valid OpenAI API key."
            ),
            "error": True,
        }
    except Neo4jError:
        response = {
            "role": "assistant",
            "content": (
                "I couldn't connect to Neo4j. Check that the database is running "
                "and that its URI and credentials in `.env` are correct."
            ),
            "error": True,
        }
    except OpenAIError as exc:
        response = {
            "role": "assistant",
            "content": openai_error_message(
                getattr(exc, "status_code", None),
                str(exc),
            ),
            "error": True,
        }
    except (httpx.HTTPError, TimeoutError, ConnectionError):
        response = {
            "role": "assistant",
            "content": (
                "A service could not be reached. Check your network connection, "
                "Neo4j availability, and API configuration, then try again."
            ),
            "error": True,
        }
    except ImportError:
        response = {
            "role": "assistant",
            "content": (
                "A required package is missing. Install the project dependencies "
                "with `pip install -r requirements.txt`."
            ),
            "error": True,
        }
    except ValueError:
        response = {
            "role": "assistant",
            "content": (
                "The query could not be processed. Check the configuration and "
                "try asking a concise movie-related question."
            ),
            "error": True,
        }

    st.session_state.messages.append(response)
    _render_message(response)
