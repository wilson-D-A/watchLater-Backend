from pydantic import BaseModel


class TagBase(BaseModel):
    name: str
    type: str | None = None

    class Config:
        orm_mode = True


class VideoBase(BaseModel):
    id: int
    title: str
    channelName: str
    videoLength: str | None = None
    thumbnail: str | None = None
    is_short: bool | None = None
    url: str
    category: str
    tags: list[TagBase] = []

    class Config:
        orm_mode = True


class TagPatch(BaseModel):
    concept: str | None = None
    tool: str | None = None
    topic: str | None = None


class CategoryResponse(BaseModel):
    all_videos: int
    categories: dict[str, int]
