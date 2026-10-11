"""User-facing messages for external service errors."""


def gemini_error_message(
    status_code: int | None,
    error_detail: str = "",
) -> str:
    detail = error_detail.lower()
    if status_code == 401 or "api_key_invalid" in detail or "api key not valid" in detail:
        return (
            "Google rejected the Gemini API key. Add a valid Google Gemini API "
            "key to `GEMINI_API_KEY` in `.env`; an OpenAI key will not work."
        )
    if status_code == 429:
        return (
            "Gemini is rate-limiting requests or the API quota has been reached. "
            "Wait briefly, then check your Gemini API quota and billing."
        )
    if status_code == 403:
        return (
            "This Gemini API key does not have permission to use the configured "
            "model. Check the key's project and API access."
        )
    if status_code == 404:
        provider_detail = error_detail.strip()
        if provider_detail:
            provider_detail = provider_detail[:400]
        return (
            "Google returned 404 for a Gemini model request. The default models "
            "are `gemini-3.8-flash` (chat) and `gemini-embedding-001` (embeddings); "
            "you can override them with `GEMINI_CHAT_MODEL` and "
            "`GEMINI_EMBEDDING_MODEL` in `.env`. Check the provider detail below "
            "and the models available to the API key's Google project."
            + (f"\n\nGoogle response: {provider_detail}" if provider_detail else "")
        )
    return (
        "The Gemini request failed. Check the API key, model access, and Gemini "
        "service status, then try again."
    )
