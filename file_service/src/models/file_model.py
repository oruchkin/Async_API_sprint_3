import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class FileDbModel(Base):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path_in_storage: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=True)
    short_name: Mapped[str] = mapped_column(String(24), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    bucket: Mapped[str] = mapped_column(String(255), nullable=False)

    def __init__(
        self, path_in_storage: str, filename: str, short_name: str, size: int, file_type: str, bucket: str
    ) -> None:
        self.path_in_storage = path_in_storage
        self.filename = filename
        self.short_name = short_name
        self.size = size
        self.file_type = file_type
        self.bucket = bucket

    def __repr__(self) -> str:
        return f"<id {self.id}>"
