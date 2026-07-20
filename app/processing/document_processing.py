from app.core.log import logger
from unstructured.partition.auto import partition
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def extract_and_chunk(file_path: str) -> list[dict]:
    elements = partition(filename=file_path)

    pages: dict[int, list[str]] = {}
    for el in elements:
        page = getattr(el.metadata, "page_number", None) or 1
        pages.setdefault(page, []).append(str(el))

    chunks = []
    for page_num, texts in pages.items():
        page_text = "\n".join(texts)
        page_chunks = splitter.split_text(page_text)

        for chunk_text in page_chunks:
            chunks.append({"text": chunk_text, "page": page_num})

    logger.info(f"Извлечено {len(chunks)} чанков из {len(pages)} страниц")
    return chunks