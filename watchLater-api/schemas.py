from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field


class TagBase(BaseModel):
    name: str | None = None
    type: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CursorPayload(BaseModel):
    value: str | None = None
    id: int
    sort_by: str
    sort_order: str


class cursorResponse(BaseModel):
    items: list[VideoBase] = Field(default_factory=list)
    next_cursor: CursorPayload | None = None
    has_next_page: bool | None = None

    model_config = ConfigDict(from_attributes=True)


class VideoBase(BaseModel):
    id: int
    title: str
    channelName: str
    videoLength: str | None = None
    thumbnail: str | None = None
    is_short: bool | None = None
    url: str
    category: str
    tags: list[TagBase] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class TagPatch(BaseModel):
    concept: str | None = None
    tool: str | None = None
    topic: str | None = None


class CategoryResponse(BaseModel):
    all_videos: int
    categories: dict[str, int]
