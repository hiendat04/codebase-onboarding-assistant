import sys

from src.store import get_store, search

if __name__ == "__main__":
    for doc in search(get_store(), sys.argv[1]):
        m = doc.metadata
        snippet = doc.page_content.split("\n", 1)[-1][:150].replace("\n", " ")  # skip the file header line
        print(f"{m['path']}:{m['start_line']}-{m['end_line']}  {m['symbol']}\n    {snippet}\n")
