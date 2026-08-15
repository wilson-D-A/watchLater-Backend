from sqlalchemy.orm import Session

from crud import seed_videos_from_file, data, add_thumbnail_to_video, get_all_videos
from models import Video
from sqlalchemy import select, func
from database import engine


def seed_videos(session: Session):
    with Session(engine) as session:
        before_count = session.scalar(select(func.count(Video.id))) or 0
        seed_videos_from_file(session, data)
        after_count = session.scalar(select(func.count(Video.id))) or 0

    created = after_count - before_count
    print(
        f"Seed completed. Videos before: {before_count}, after: {after_count}, created: {created}"
    )


def main() -> None:
    with Session(engine) as session:
        videos = get_all_videos(session)
        for video in videos:
            add_thumbnail_to_video(video)
            session.commit()


if __name__ == "__main__":
    main()
