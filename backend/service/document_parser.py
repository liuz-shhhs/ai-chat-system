import base64
import re
import zipfile
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree


MAX_UPLOAD_BYTES = 12 * 1024 * 1024
MAX_CHUNK_CHARS = 900
OVERLAP_CHARS = 120

TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".csv"}
SUPPORTED_EXTENSIONS = TEXT_EXTENSIONS | {".docx", ".pdf"}


class DocumentParseError(ValueError):
    pass


def clean_filename(filename):
    clean_name = (filename or "untitled.txt").replace("\\", "/").split("/")[-1].strip()
    return clean_name or "untitled.txt"


def decode_base64_file(content_base64):
    raw_content = content_base64 or ""

    if "," in raw_content and raw_content.strip().startswith("data:"):
        raw_content = raw_content.split(",", 1)[1]

    try:
        content = base64.b64decode(raw_content, validate=False)
    except Exception as exc:
        raise DocumentParseError("文件内容不是有效的 base64 数据。") from exc

    if len(content) == 0:
        raise DocumentParseError("文件内容为空。")

    if len(content) > MAX_UPLOAD_BYTES:
        raise DocumentParseError("文件过大，请上传 12MB 以内的文档。")

    return content


def extract_sections(filename, content):
    clean_name = clean_filename(filename)
    extension = Path(clean_name).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise DocumentParseError("当前仅支持 TXT、Markdown、CSV、DOCX 和 PDF 文档。")

    if extension in TEXT_EXTENSIONS:
        return [{"text": decode_text(content), "page_number": None}]

    if extension == ".docx":
        return [{"text": extract_docx_text(content), "page_number": None}]

    return extract_pdf_sections(content)


def decode_text(content):
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "latin-1"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue

    raise DocumentParseError("无法识别文档编码。")


def extract_docx_text(content):
    try:
        archive = zipfile.ZipFile(BytesIO(content))
    except zipfile.BadZipFile as exc:
        raise DocumentParseError("DOCX 文件格式无效。") from exc

    paragraphs = []
    text_tag = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"
    paragraph_tag = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"

    for xml_name in ("word/document.xml", "word/footnotes.xml", "word/endnotes.xml"):
        if xml_name not in archive.namelist():
            continue

        root = ElementTree.fromstring(archive.read(xml_name))

        for paragraph in root.iter(paragraph_tag):
            text_parts = [
                node.text
                for node in paragraph.iter(text_tag)
                if node.text
            ]
            text = "".join(text_parts).strip()

            if text:
                paragraphs.append(text)

    return "\n".join(paragraphs)


def extract_pdf_sections(content):
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise DocumentParseError("解析 PDF 需要安装 pypdf，请先运行 pip install -r requirements.txt。") from exc

    try:
        reader = PdfReader(BytesIO(content))
    except Exception as exc:
        raise DocumentParseError("PDF 文件格式无效或无法读取。") from exc

    sections = []

    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            sections.append({"text": text, "page_number": index})

    return sections


def chunk_sections(sections):
    chunks = []

    for section in sections:
        page_number = section.get("page_number")

        for content in chunk_text(section.get("text", "")):
            chunks.append(
                {
                    "chunk_index": len(chunks),
                    "content": content,
                    "page_number": page_number,
                }
            )

    if not chunks:
        raise DocumentParseError("没有从文档中解析到可检索文本。")

    return chunks


def chunk_text(text, max_chars=MAX_CHUNK_CHARS):
    normalized = re.sub(r"\r\n?", "\n", text or "")
    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n|\n", normalized)
        if paragraph.strip()
    ]

    chunks = []
    current = []
    current_length = 0

    def flush_current():
        nonlocal current, current_length

        if current:
            chunks.append("\n".join(current).strip())
            current = []
            current_length = 0

    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            flush_current()
            chunks.extend(slice_long_text(paragraph, max_chars))
            continue

        next_length = current_length + len(paragraph) + (1 if current else 0)

        if next_length > max_chars:
            flush_current()

        current.append(paragraph)
        current_length += len(paragraph) + (1 if current_length else 0)

    flush_current()

    return chunks


def slice_long_text(text, max_chars):
    pieces = []
    start = 0
    clean_text = text.strip()

    while start < len(clean_text):
        end = min(start + max_chars, len(clean_text))
        piece = clean_text[start:end].strip()

        if piece:
            pieces.append(piece)

        if end >= len(clean_text):
            break

        start = max(end - OVERLAP_CHARS, start + 1)

    return pieces
