import importlib
import sys

import pytest

MODULES = ["chromadb", "tree_sitter", "tree_sitter_go", "ragas", "langchain",
           "langchain_chroma", "langchain_huggingface", "langchain_text_splitters",
           "sentence_transformers", "streamlit", "dotenv"]


def test_python_is_312():
    assert sys.version_info[:2] == (3, 12)


@pytest.mark.parametrize("name", MODULES)
def test_module_imports(name):
    importlib.import_module(name)
