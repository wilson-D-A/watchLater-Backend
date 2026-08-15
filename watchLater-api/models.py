from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Video(Base):
    __tablename__ = "video"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    channelName: Mapped[str]
    videoLength: Mapped[str | None] = mapped_column(nullable=True)
    url: Mapped[str]
    thumbnail: Mapped[str | None] = mapped_column(nullable=True)
    is_short: Mapped[bool | None] = mapped_column(nullable=True)
    category: Mapped[str]
    tags: Mapped[List["Tag"]] = relationship(
        back_populates="video", order_by="Tag.id", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Video(id={self.id!r}, title={self.title!r}, channelName={self.channelName!r})"


class Tag(Base):
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(default=None, nullable=True)
    type: Mapped[str | None] = mapped_column(default=None, nullable=True)
    video_id: Mapped[int] = mapped_column(ForeignKey("video.id"))
    video: Mapped["Video"] = relationship(back_populates="tags")

    def __repr__(self) -> str:
        return f"Tag(id={self.id!r}, name={self.name!r}, type={self.type!r}, video_id={self.video_id!r})"
