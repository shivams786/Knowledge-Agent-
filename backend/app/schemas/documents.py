from datetime import datetime

from pydantic import BaseModel


class DocumentRead(BaseModel):
    id: int
    filename: str
    file_type: str
    source_path: str
    checksum: str
    access_level: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentDetail(DocumentRead):
    extracted_text: str


class UploadResponse(BaseModel):
    document: DocumentRead
    chunk_count: int
    duplicate: bool = False
    message: str
