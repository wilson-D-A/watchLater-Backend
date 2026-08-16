from fastapi import FastAPI, Depends, Query
from schemas import TagBase, VideoBase, TagPatch, CategoryResponse, cursorResponse
from typing import Annotated, Literal
from contextlib import asynccontextmanager
import os
from database import get_session, init_db, close_connector
from crud import (
    get_all_tags_in_category,
    list_categories,
    patch_tag_from_video,
    get_video_by_id,
    delete_video_from_db,
    get_all_videos_cursor_pg,
)
from sqlalchemy.orm import Session


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("INIT_DB_ON_STARTUP", "false").lower() == "true":
        init_db()
    try:
        yield
    finally:
        close_connector()


app = FastAPI(lifespan=lifespan)


@app.get("/videos", response_model=cursorResponse)
async def get_videos(
    session: Annotated[Session, Depends(get_session)],
    cursor_value: str | None = Query(default=None),
    cursor_id: int | None = Query(default=None),
    category: str | None = Query(default=None),
    tag: list[str] | None = Query(default=None),
    sort_by: Literal["title", "channelName"] = Query(default="title"),
    sort_order: Literal["asc", "desc"] = Query(default="asc"),
):
    return get_all_videos_cursor_pg(
        session,
        cursor_value,
        cursor_id,
        limit=20,
        category=category,
        tag=tag,
        sort_by=sort_by,
        sort_order=sort_order,
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
