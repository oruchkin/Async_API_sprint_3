from datetime import datetime

from pydantic import BaseModel


class Template(BaseModel):
    id: str
    subject: str
    body: str
    created_at: datetime
