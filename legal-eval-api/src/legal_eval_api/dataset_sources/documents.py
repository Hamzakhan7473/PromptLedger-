"""Extract and chunk raw contract documents into labeling-template excerpts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, UploadFile

# CUAD caps excerpts at 8000 chars (legaleval.data.cuad.DEFAULT_MAX_CHARS).
TARGET_MAX_CHARS = 8000
MIN_CHUNK_CHARS = 400
MAX_PDF_PAGES = 200
MAX_EXCERPTS = 500
MAX_FILE_BYTES = 20 * 1024 * 1024  # 20 MiB per file
MAX_FILES_PER_REQUEST = 10

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@dataclass(frozen=True)
class CandidateExcerpt:
    id: str
    contract_excerpt: str
    contract_title: str
    source_filename: str
    source_reference: str


def _normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _slug_stem(filename: str) -> str:
    stem = Path(filename).stem.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
    return slug or "document"


def extract_pdf_text(data: bytes, *, filename: str) -> list[tuple[str, str]]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail="PDF extraction requires the `pypdf` package on the API server.",
        ) from exc

    try:
        reader = PdfReader(BytesIO(data))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=400,
            detail=f"Could not read PDF {filename!r}: {exc}",
        ) from exc

    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(
                status_code=400,
                detail=f"PDF {filename!r} is encrypted and could not be decrypted.",
            ) from exc

    page_texts: list[tuple[str, str]] = []
    for page_no, page in enumerate(reader.pages, start=1):
        if page_no > MAX_PDF_PAGES:
            break
        try:
            text = page.extract_text() or ""
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract text from page {page_no} of {filename!r}: {exc}",
            ) from exc
        cleaned = _normalize_whitespace(text)
        if cleaned:
            page_texts.append((f"page {page_no}", cleaned))
    return page_texts


def extract_docx_text(data: bytes, *, filename: str) -> list[tuple[str, str]]:
    try:
        from docx import Document
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail="DOCX extraction requires the `python-docx` package on the API server.",
        ) from exc

    try:
        document = Document(BytesIO(data))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=400,
            detail=f"Could not read DOCX {filename!r}: {exc}",
        ) from exc

    paragraphs: list[tuple[str, str]] = []
    for index, paragraph in enumerate(document.paragraphs, start=1):
        cleaned = _normalize_whitespace(paragraph.text)
        if cleaned:
            paragraphs.append((f"paragraph {index}", cleaned))
    return paragraphs


def extract_txt_text(data: bytes, *, filename: str) -> list[tuple[str, str]]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Text file {filename!r} must be UTF-8.",
        ) from exc
    cleaned = _normalize_whitespace(text)
    if not cleaned:
        return []
    return [("document", cleaned)]


def chunk_page_sections(sections: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Merge short PDF pages and split long ones to stay near TARGET_MAX_CHARS."""
    if not sections:
        return []

    merged: list[tuple[str, str]] = []
    buffer_ref: list[str] = []
    buffer_text: list[str] = []

    def flush() -> None:
        if not buffer_text:
            return
        merged.append(("; ".join(buffer_ref), "\n\n".join(buffer_text)))
        buffer_ref.clear()
        buffer_text.clear()

    for ref, text in sections:
        if len(text) > TARGET_MAX_CHARS:
            flush()
            start = 0
            part = 1
            while start < len(text):
                end = min(start + TARGET_MAX_CHARS, len(text))
                merged.append((f"{ref} (part {part})", text[start:end]))
                start = end
                part += 1
            continue

        candidate_len = sum(len(chunk) for chunk in buffer_text) + len(text)
        if buffer_text and candidate_len > TARGET_MAX_CHARS:
            flush()

        buffer_ref.append(ref)
        buffer_text.append(text)
        if sum(len(chunk) for chunk in buffer_text) >= MIN_CHUNK_CHARS:
            flush()

    flush()
    return merged


def chunk_paragraph_sections(sections: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Paragraph/section chunking for DOCX and plain text."""
    if not sections:
        return []

    chunks: list[tuple[str, str]] = []
    current_refs: list[str] = []
    current_parts: list[str] = []
    current_len = 0

    def flush() -> None:
        nonlocal current_len
        if not current_parts:
            return
        chunks.append(("; ".join(current_refs), "\n\n".join(current_parts)))
        current_refs.clear()
        current_parts.clear()
        current_len = 0

    for ref, text in sections:
        if len(text) > TARGET_MAX_CHARS:
            flush()
            start = 0
            part = 1
            while start < len(text):
                end = min(start + TARGET_MAX_CHARS, len(text))
                chunks.append((f"{ref} (part {part})", text[start:end]))
                start = end
                part += 1
            continue

        extra = len(text) if not current_parts else len(text) + 2
        if current_parts and current_len + extra > TARGET_MAX_CHARS:
            flush()

        current_refs.append(ref)
        current_parts.append(text)
        current_len += extra
        if current_len >= MIN_CHUNK_CHARS:
            flush()

    flush()
    return chunks


def excerpts_from_upload(filename: str, data: bytes) -> list[CandidateExcerpt]:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type {suffix!r} for {filename!r}. "
                f"Use one of: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            ),
        )

    if suffix == ".pdf":
        sections = extract_pdf_text(data, filename=filename)
        chunks = chunk_page_sections(sections)
    elif suffix == ".docx":
        sections = extract_docx_text(data, filename=filename)
        chunks = chunk_paragraph_sections(sections)
    else:
        sections = extract_txt_text(data, filename=filename)
        if sections:
            chunks = chunk_paragraph_sections(
                _split_text_paragraphs(sections[0][1]),
            )
        else:
            chunks = []

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail=f"No extractable text found in {filename!r}.",
        )

    slug = _slug_stem(filename)
    excerpts: list[CandidateExcerpt] = []
    for index, (reference, text) in enumerate(chunks, start=1):
        excerpts.append(
            CandidateExcerpt(
                id=f"{slug}-{index:03d}",
                contract_excerpt=text,
                contract_title=Path(filename).stem,
                source_filename=filename,
                source_reference=reference,
            ),
        )
    return excerpts


def _split_text_paragraphs(text: str) -> list[tuple[str, str]]:
    parts = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    if not parts:
        return []
    return [(f"section {index}", part) for index, part in enumerate(parts, start=1)]


def template_row(candidate: CandidateExcerpt) -> dict[str, object]:
    """Labeling template row — not a valid EvalExample until the user fills labels."""
    return {
        "id": candidate.id,
        "contract_excerpt": candidate.contract_excerpt,
        "contract_title": candidate.contract_title,
        "category": "",
        "present": None,
        "gold_spans": [],
    }


def render_template_jsonl(candidates: list[CandidateExcerpt]) -> str:
    lines = [json.dumps(template_row(candidate), ensure_ascii=False) for candidate in candidates]
    return "\n".join(lines) + "\n"


async def read_upload_bytes(upload: UploadFile, *, max_bytes: int = MAX_FILE_BYTES) -> bytes:
    if not upload.filename:
        raise HTTPException(status_code=400, detail="Each uploaded file must have a filename.")
    body = await upload.read()
    if len(body) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=(
                f"File {upload.filename!r} exceeds the {max_bytes // (1024 * 1024)} MiB limit."
            ),
        )
    if not body:
        raise HTTPException(status_code=400, detail=f"File {upload.filename!r} is empty.")
    return body


async def build_candidates_from_uploads(files: list[UploadFile]) -> list[CandidateExcerpt]:
    if not files:
        raise HTTPException(status_code=400, detail="Upload at least one PDF, DOCX, or TXT file.")
    if len(files) > MAX_FILES_PER_REQUEST:
        raise HTTPException(
            status_code=400,
            detail=f"At most {MAX_FILES_PER_REQUEST} files per request.",
        )

    all_excerpts: list[CandidateExcerpt] = []
    seen_ids: set[str] = set()
    for upload in files:
        data = await read_upload_bytes(upload)
        excerpts = excerpts_from_upload(upload.filename or "document", data)
        for excerpt in excerpts:
            unique_id = excerpt.id
            counter = 2
            while unique_id in seen_ids:
                unique_id = f"{excerpt.id}-{counter}"
                counter += 1
            seen_ids.add(unique_id)
            if unique_id != excerpt.id:
                excerpt = CandidateExcerpt(
                    id=unique_id,
                    contract_excerpt=excerpt.contract_excerpt,
                    contract_title=excerpt.contract_title,
                    source_filename=excerpt.source_filename,
                    source_reference=excerpt.source_reference,
                )
            all_excerpts.append(excerpt)
            if len(all_excerpts) >= MAX_EXCERPTS:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Extracted excerpt limit ({MAX_EXCERPTS}) exceeded. "
                        "Upload fewer or smaller documents."
                    ),
                )

    if not all_excerpts:
        raise HTTPException(status_code=400, detail="No extractable text found in uploaded files.")
    return all_excerpts
