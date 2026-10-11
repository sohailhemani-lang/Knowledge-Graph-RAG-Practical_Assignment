import csv
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("NEO4J_URI", "bolt://127.0.0.1:7687")
os.environ.setdefault("NEO4J_USER", "test-user")
os.environ.setdefault("NEO4J_PASSWORD", "test-password")
os.environ.setdefault("GEMINI_API_KEY", "test-key")

import evaluate
from error_messages import gemini_error_message
import graph_retriever
import rag_chain
import router
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda


class HybridRagRequirementTests(unittest.TestCase):
    def test_router_reads_gemini_text_content_blocks(self):
        llm = RunnableLambda(
            lambda _: AIMessage(content=[{"type": "text", "text": "graph"}])
        )
        with patch.object(router, "_llm", llm):
            decision = router._llm_route("Find movies starring this actor")

        self.assertEqual(decision, "graph")

    def test_router_still_reads_string_responses(self):
        llm = RunnableLambda(lambda _: AIMessage(content="vector"))
        with patch.object(router, "_llm", llm):
            decision = router._llm_route("Find a movie with an unusual plot")

        self.assertEqual(decision, "vector")

    def test_router_rejects_non_text_gemini_response(self):
        llm = RunnableLambda(lambda _: AIMessage(content=[]))
        with patch.object(router, "_llm", llm):
            with self.assertRaisesRegex(ValueError, "returned no text"):
                router._llm_route("Find a movie with an unusual plot")

    def test_empty_query_is_rejected(self):
        with self.assertRaises(ValueError):
            rag_chain.run_hybrid_rag("  ", verbose=False)

    def test_empty_vector_results_return_helpful_answer_without_calling_llm(self):
        with patch.object(rag_chain, "route", return_value="vector"), patch.object(
            rag_chain, "similarity_search", return_value=[]
        ), patch.object(rag_chain, "_chain") as chain:
            result = rag_chain.run_hybrid_rag("Find a movie about an unknown topic")

        self.assertIn("couldn't find matching movie information", result["answer"])
        chain.invoke.assert_not_called()

    def test_graph_no_match_returns_helpful_answer_without_calling_llm(self):
        with patch.object(rag_chain, "route", return_value="graph"), patch.object(
            rag_chain,
            "graph_retrieve",
            return_value="No matching movie was found in the dataset.",
        ), patch.object(rag_chain, "_chain") as chain:
            result = rag_chain.run_hybrid_rag("Who directed Avatar?")

        self.assertIn("couldn't find matching movie information", result["answer"])
        chain.invoke.assert_not_called()

    def test_unknown_movie_question_does_not_fall_back_to_entire_catalog(self):
        result = graph_retriever.graph_retrieve("Who directed Avatar?")
        self.assertEqual(
            result,
            "No matching movie or director was found in the dataset.",
        )

    def test_unknown_cast_question_returns_no_match(self):
        result = graph_retriever.graph_retrieve("Who acted in Avatar?")
        self.assertEqual(result, "No matching movie was found in the dataset.")

    def test_known_movie_cast_query_uses_movie_lookup(self):
        with patch.object(
            graph_retriever, "get_actors_in_movie", return_value="cast"
        ) as lookup:
            result = graph_retriever.graph_retrieve("Who acted in The Matrix?")

        self.assertEqual(result, "cast")
        lookup.assert_called_once_with("The Matrix")

    def test_evaluation_covers_at_least_ten_queries_and_unknown_title(self):
        self.assertGreaterEqual(len(evaluate.ALL_QUESTIONS), 10)
        self.assertTrue(
            any("Avatar" in item["question"] for item in evaluate.ALL_QUESTIONS)
        )

    def test_app_explains_gemini_quota_or_rate_limit(self):
        message = gemini_error_message(429)
        self.assertIn("rate-limiting", message)
        self.assertIn("quota", message)

    def test_app_explains_invalid_gemini_key(self):
        message = gemini_error_message(
            400,
            "API_KEY_INVALID: API key not valid",
        )
        self.assertIn("Google rejected the Gemini API key", message)
        self.assertIn("OpenAI key will not work", message)

    def test_app_explains_unauthorized_gemini_key(self):
        message = gemini_error_message(401)
        self.assertIn("Google rejected the Gemini API key", message)

    def test_app_includes_google_model_not_found_details(self):
        message = gemini_error_message(
            404,
            "models/gemini-3.8-flash is not found for API version v1beta",
        )
        self.assertIn("GEMINI_CHAT_MODEL", message)
        self.assertIn("models/gemini-3.8-flash is not found", message)

    def test_default_gemini_chat_model_uses_current_supported_model(self):
        import config

        self.assertEqual(config.GEMINI_CHAT_MODEL, "gemini-3.8-flash")

    def test_evaluation_report_writer_records_answer_and_outcome_fields(self):
        row = {
            "question": "Who directed Inception?",
            "expected_answer": "Christopher Nolan directed Inception.",
            "actual_answer": "Christopher Nolan directed Inception.",
            "expected_retriever": "graph",
            "actual_retriever": "graph",
            "route_correct": True,
            "expected_facts_found": True,
            "relevance_review": "Pending manual review",
            "response_time_seconds": 0.42,
        }
        with tempfile.TemporaryDirectory() as directory:
            report_path = Path(directory) / "evaluation_report.csv"
            evaluate.write_evaluation_report([row], report_path)
            with report_path.open(encoding="utf-8", newline="") as report_file:
                saved_row = next(csv.DictReader(report_file))

        self.assertEqual(saved_row["actual_answer"], row["actual_answer"])
        self.assertEqual(saved_row["actual_retriever"], "graph")
        self.assertEqual(saved_row["expected_facts_found"], "True")
        self.assertEqual(saved_row["relevance_review"], "Pending manual review")


if __name__ == "__main__":
    unittest.main()
