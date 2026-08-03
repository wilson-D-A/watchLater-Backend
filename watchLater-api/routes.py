from fastapi import FastAPI, Depends, Query
from schemas import TagBase, VideoBase, TagPatch, CategoryResponse
from typing import Annotated
from database import get_session
from crud import (
    get_all_tags_in_category,
    list_categories,
    patch_tag_from_video,
    get_video_by_id,
    delete_video_from_db,
    get_all_videos_cursor_pg,
)
from sqlalchemy.orm import Session

app = FastAPI()


@app.get("/videos", response_model=list[VideoBase])
async def get_videos(
    session: Annotated[Session, Depends(get_session)],
    cursor: int | None = Query(default=0),
    category: str | None = Query(default=None),
    tag: list[str] | None = Query(default=None),
):
    return get_all_videos_cursor_pg(
        session,
        cursor,
        limit=20,
        category=category,
        tag=tag,
    )


@app.get("/categories", response_model=CategoryResponse)
async def get_categories(
    session: Annotated[Session, Depends(get_session)],
):
    return list_categories(session)


@app.get("/tags_by_category", response_model=list[TagBase])
async def get_tags_by_category(
    category: str,
    session: Annotated[Session, Depends(get_session)],
):
    return get_all_tags_in_category(session, category=category)


@app.patch("/videos/{video_id}", response_model=VideoBase)
async def update_video(
    video_id: int,
    video_data: TagPatch,
    session: Annotated[Session, Depends(get_session)],
):

    video = get_video_by_id(session, video_id)
    video_data_dict = video_data.model_dump(exclude_unset=True)
    patch_tag_from_video(session, video, video_data_dict)

    return video


@app.delete("/videos/{video_id}", response_model=dict[str, str])
async def delete_video(
    video_id: int,
    session: Annotated[Session, Depends(get_session)],
):
    video = get_video_by_id(session, video_id)

    if not video:
        return {"error": "Video not found"}

    delete_video_from_db(session, video)
    return {"message": f"Video with ID {video_id} has been deleted."}
