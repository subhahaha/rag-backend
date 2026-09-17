import re

from langchain_text_splitters import RecursiveCharacterTextSplitter


def recursive_chunking(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    return splitter.split_text(text)


def sentence_chunking(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    return [sentence.strip() for sentence in sentences if sentence.strip()]


def chunk_text(text: str, strategy: str) -> list[str]:
    if strategy == "recursive":
        return recursive_chunking(text)

    if strategy == "sentence":
        return sentence_chunking(text)

    raise ValueError(
        "Invalid chunking strategy. Choose 'recursive' or 'sentence'."
    )