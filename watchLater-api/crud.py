from models import Video, Tag
from sqlalchemy import select
from sqlalchemy.orm import Session

# json_path = Path("api") / "watchlater_grouped.json"

# with open(json_path, "r") as f:
#     data = json.loads(f.read())


def create_video(session: Session, data: list[dict]):
    video = None
    for video_data in data:
        video = Video(
            title=video_data.get("title"),
            channelName=video_data.get("channelName"),
            videoLength=video_data.get("videoLength"),
            url=video_data.get("url"),
            category=video_data.get("category"),
        )
        session.add(video)

        for tag_name in video_data.get("tag", []):
            tag = Tag(name=tag_name, video=video)
            session.add(tag)

        session.commit()
        session.refresh(video)

    return video


# def seed_videos_from_file(session: Session):
#     create_video(session=session, data=data)


def get_video_by_id(session: Session, video_id: int):
    return session.get(Video, video_id)


def get_tag_by_video(session: Session, video_id: int):
    return session.execute(select(Tag).where(Tag.video_id == video_id)).scalars().all()


def get_all_videos(session: Session):
    return session.execute(select(Video)).scalars().all()


def get_all_videos_cursor_pg(session: Session, cursor, limit: int = 20):
    stmt = select(Video).order_by(Video.id)
    if cursor:
        stmt = stmt.where(Video.id > cursor)

    stmt = stmt.limit(limit)
    return session.execute(stmt).scalars().all()


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
