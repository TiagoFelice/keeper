from pydantic import BaseModel


class ObjectCreate(BaseModel):
    content: bytes
    content_type: str


class ObjectResponse(BaseModel):
    key: str
    etag: str
    content_type: str
    last_modified: str
