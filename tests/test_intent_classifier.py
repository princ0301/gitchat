from langchain_core.messages import AIMessage
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from app.agent.nodes.intent_classifier import IntentClassifierNode, INTENT_BROAD, INTENT_TARGETED, INTENT_IMPACT_ANALYSIS


class FakeLLMProvider:
    def __init__(self, response_text: str):
        self._chat_model = FakeListChatModel(responses=[response_text])

    def get_chat_model(self):
        return self._chat_model


def make_state(query: str) -> dict:
    return {
        "query": query,
        "chat_history": [],
        "repo_id": "test-repo",
        "intent": "",
        "retrieval_results": [],
        "answer": "",
        "confidence": 0.0,
        "retrieval_attempts": 0,
        "vector_k": 5,
        "expansion_hops": 1,
    }


def test_classifies_broad_intent():
    provider = FakeLLMProvider("broad")
    node = IntentClassifierNode(provider)

    result = node(make_state("how does authentication work"))
    assert result["intent"] == INTENT_BROAD


def test_classifies_targeted_intent():
    provider = FakeLLMProvider("targeted")
    node = IntentClassifierNode(provider)

    result = node(make_state("what does the login function do"))
    assert result["intent"] == INTENT_TARGETED


def test_classifies_impact_analysis_intent():
    provider = FakeLLMProvider("impact_analysis")
    node = IntentClassifierNode(provider)

    result = node(make_state("what would break if I change this file"))
    assert result["intent"] == INTENT_IMPACT_ANALYSIS


def test_handles_response_with_extra_text():
    provider = FakeLLMProvider("The category is: targeted")
    node = IntentClassifierNode(provider)

    result = node(make_state("trace the login flow"))
    assert result["intent"] == INTENT_TARGETED


def test_falls_back_to_broad_on_unparseable_response():
    provider = FakeLLMProvider("I'm not sure what category this is")
    node = IntentClassifierNode(provider)

    result = node(make_state("some ambiguous question"))
    assert result["intent"] == INTENT_BROAD


def test_returns_only_intent_key():
    provider = FakeLLMProvider("broad")
    node = IntentClassifierNode(provider)

    result = node(make_state("how does this work"))
    assert set(result.keys()) == {"intent"}