from src import config
from src.generation.llm import get_llm


def test_get_llm_uses_config_model():
    llm = get_llm()  # creating it does not contact Ollama
    assert llm.model == config.LLM_MODEL
    assert llm.temperature == 0
