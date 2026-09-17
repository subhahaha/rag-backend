import fitz
from fastapi import UploadFile


async def extract_text(file: UploadFile) -> str:
    filename = file.filename or ""

    if filename.lower().endswith(".txt"):
        content = await file.read()
        text = content.decode("utf-8")

        if not text.strip():
            raise ValueError("Document contains no text.")

        return text

    if filename.lower().endswith(".pdf"):
        content = await file.read()

        document = fitz.open(stream=content, filetype="pdf")

        text = ""

        for page in document:
            text += page.get_text()

        document.close()

        if not text.strip():
            raise ValueError("Document contains no text.")

        return text

        

    raise ValueError("Unsupported file type")