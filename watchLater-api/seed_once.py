from sqlalchemy.orm import Session

from crud import (
    get_all_tags_in_category,
)
from models import Video
from sqlalchemy import select, func
from database import close_connector, engine


def seed_videos(session: Session):
    with Session(engine) as session:
        before_count = session.scalar(select(func.count(Video.id))) or 0
        # seed_videos_from_file(session, data)
        after_count = session.scalar(select(func.count(Video.id))) or 0

    created = after_count - before_count
    print(
        f"Seed completed. Videos before: {before_count}, after: {after_count}, created: {created}"
    )


def main() -> None:
    try:
        with Session(engine) as session:
            print(get_all_tags_in_category(session, category="Engineering Practices"))
    finally:
        engine.dispose()
        close_connector()


if __name__ == "__main__":
    main()
