from pydantic import BaseModel


class TagBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class VideoBase(BaseModel):
    id: int
    title: str
    channelName: str
    videoLength: str
    url: str
    category: str
    tags: list[TagBase] = []

    class Config:
        orm_mode = True


class TagPatch(BaseModel):
    concept: str | None = None
    tool: str | None = None
    topic: str | None = None
