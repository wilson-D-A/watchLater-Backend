from models import Video, Tag
from sqlalchemy import func, select
from sqlalchemy.orm import Session

# json_path = Path() / "liked_playlist.json"

# with open(json_path, "r") as f:
#     data = json.loads(f.read())

import re


def get_youtube_id(url: str) -> str | None:
    match = re.search(r"(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None


def add_thumbnail_to_video(video: Video):
    # query all videos in the database
    # for each video, if the video is a short, set the thumbnail to the thumbnail in the data, else set it to the youtube thumbnail
    if video.is_short:
        data_video = next((item for item in data if item["url"] == video.url), None)
        if data_video and "thumbnail" in data_video:
            video.thumbnail = data_video["thumbnail"]
    else:
        video.thumbnail = (
            f"https://img.youtube.com/vi/{get_youtube_id(video.url)}/hqdefault.jpg"
        )
    return f"Thumbnail for video {video.id} set to {video.thumbnail}"


def create_video(session: Session, data: list[dict]):
    video = None
    types = ["concept", "tool", "topic"]
    for video_data in data:
        video = Video(
            title=video_data.get("title"),
            channelName=video_data.get("channelName"),
            videoLength=video_data.get("videoLength", None),
            url=video_data.get("url"),
            category=video_data.get("category"),
            is_short=video_data.get("is_short", False),
        )
        session.add(video)

        for tag_name in video_data.get("tag", []):
            for tag_type in types:
                tag = Tag(name=tag_name, type=tag_type, video=video)
                session.add(tag)

        session.commit()
        session.refresh(video)

    return video


def seed_tag_types(session: Session):
    get_all_videos = session.execute(select(Video)).scalars().all()
    for i, video in enumerate(get_all_videos):
        for j, tag in enumerate(video.tags):
            if j == 0:
                tag.type = "concept"
            elif j == 1:
                tag.type = "tool"
            elif j == 2:
                tag.type = "topic"

    session.commit()
    print(video)


def seed_videos_from_file(session: Session, data: list[dict]):
    create_video(session, data)


def get_video_by_id(session: Session, video_id: int):
    return session.get(Video, video_id)


def get_tag_by_video(session: Session, video_id: int):
    return session.execute(select(Tag).where(Tag.video_id == video_id)).scalars().all()


def get_all_tags_in_category(session: Session, category: str):
    return (
        session.execute(select(Tag).join(Video).where(Video.category == category))
        .scalars()
        .all()
    )


def filter_videos(
    session: Session, category: str | None = None, tag: list[str] | None = None
):
    stmt = select(Video)

    return session.execute(stmt).scalars().all()


def get_all_videos(session: Session):
    return session.execute(select(Video)).scalars().all()


def get_all_videos_cursor_pg(
    session: Session,
    cursor,
    limit: int = 20,
    category: str | None = None,
    tag: list[str] | None = None,
):
    stmt = select(Video).order_by(Video.id)
    if cursor:
        stmt = stmt.where(Video.id > cursor)
    if category:
        stmt = stmt.where(Video.category == category)
    if tag:
        stmt = stmt.join(Video.tags).where(Tag.name.in_(tag))

    stmt = stmt.limit(limit)
    return session.execute(stmt).scalars().all()


def list_categories(session: Session):
    categories = session.execute(select(Video.category).distinct()).scalars().all()
    category_dict = {}
    for category in categories:
        stmt = select(func.count(Video.id)).where(Video.category == category)
        category_dict[category] = session.execute(stmt).scalar()

    return {
        "all_videos": session.scalar(select(func.count(Video.id))),
        "categories": category_dict,
    }


def patch_tag_from_video(session: Session, video: Video, new_tags: dict):
    if not video:
        return []

    ordered_tags = list(video.tags)
    updates = (("concept", 0), ("tool", 1), ("topic", 2))

    for field_name, index in updates:
        if index < len(ordered_tags):
            new_value = new_tags.get(field_name)
            if new_value is not None:
                ordered_tags[index].name = new_value

    print(f"Updated tags for video {video.id}: {[tag.name for tag in ordered_tags]}")
    session.commit()
    session.refresh(video)
    return video.tags


def delete_video_from_db(session: Session, video: Video):
    if video:
        session.delete(video)
        session.commit()
