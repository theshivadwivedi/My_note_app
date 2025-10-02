from pydantic import BaseModel

class Note(BaseModel):
    tittle: str
    content: str
    important: bool | None