from pydantic import BaseModel, Field


class FileIn(BaseModel):
    file_name: str = Field(min_length=1, max_length=200)
    mime_type: str = Field(min_length=1, max_length=100)
    data_base64: str = Field(min_length=1)
