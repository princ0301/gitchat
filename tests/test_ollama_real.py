from app.providers.llm.factory import get_llm_provider


def test_ollama_real_invoke():
    provider = get_llm_provider("ollama")
    chat_model = provider.get_chat_model()
    response = chat_model.invoke("Reply with exactly the word: pong")

    print(f"response: {response.content}")
    assert response.content