"""User-facing messages for external service errors."""


def openai_error_message(
    status_code: int | None,
    error_detail: str = "",
) -> str:
    detail = error_detail.strip()
    if status_code == 401:
        return (
            "OpenAI rejected the API key. Add a valid OpenAI key to "
            "`OPENAI_API_KEY` in `.env`."
        )
    if status_code == 429:
        return (
            "OpenAI is rate-limiting requests or the API quota has been reached. "
            "Wait briefly, then check your OpenAI usage, limits, and billing."
        )
    if status_code == 403:
        return (
            "OpenAI denied access to the configured model. Check the API key's "
            "project permissions and model access."
        )
    if status_code == 404:
        provider_detail = detail[:400]
        return (
            "OpenAI could not find the configured model. Check "
            "`OPENAI_CHAT_MODEL` and `OPENAI_EMBEDDING_MODEL` in `.env`."
            + (f"\n\nOpenAI response: {provider_detail}" if provider_detail else "")
        )
    return (
        "The OpenAI request failed. Check the API key, model access, and OpenAI "
        "service status, then try again."
    )
