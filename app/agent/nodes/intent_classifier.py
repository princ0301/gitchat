from app.agent.state import AgentState
from app.core.interfaces.llm_provider import LLMProvider

INTENT_BROAD = "broad"
INTENT_TARGETED = "targeted"
INTENT_IMPACT_ANALYSIS = "impact_analysis"

VALID_INTENTS = {INTENT_BROAD, INTENT_TARGETED, INTENT_IMPACT_ANALYSIS}

CLASSIFICATION_PROMPT = """Classify the following code question into exactly one category.

Categories:
- broad: general questions about how something works, architecture, or design (e.g. "how does auth work", "explain the routing system")
- targeted: questions about a specific function, file, or trace through specific code (e.g. "what does the login function do", "trace the request from frontend to db")
- impact_analysis: questions about dependencies or consequences of changes (e.g. "what would break if I change this file", "what depends on this function")

Respond with exactly one word: broad, targeted, or impact_analysis.

Question: {query}
"""


class IntentClassifierNode:
    def __init__(self, llm_provider: LLMProvider):
        self._llm_provider = llm_provider

    def __call__(self, state: AgentState) -> dict:
        chat_model = self._llm_provider.get_chat_model()
        prompt = CLASSIFICATION_PROMPT.format(query=state["query"])
        response = chat_model.invoke(prompt)
        intent = self._parse_intent(response.content)
        return {"intent": intent}

    def _parse_intent(self, raw_response: str) -> str:
        normalized = raw_response.strip().lower()
        for intent in VALID_INTENTS:
            if intent in normalized:
                return intent
        return INTENT_BROAD