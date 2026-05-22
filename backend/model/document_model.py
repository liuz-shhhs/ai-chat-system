from typing import Optional

from pydantic import BaseModel


class DocumentUploadRequest(BaseModel):
    filename: str
    content_base64: str
    content_type: Optional[str] = None
