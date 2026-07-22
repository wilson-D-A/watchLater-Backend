from sqlalchemy import func, select
from sqlalchemy.orm import Session

from crud import seed_videos_from_file
from database import engine
from models import Video


def main() -> None:
    with Session(engine) as session:
        before_count = session.scalar(select(func.count(Video.id))) or 0
        seed_videos_from_file(session)
        after_count = session.scalar(select(func.count(Video.id))) or 0

    created = after_count - before_count
    print(
        f"Seed completed. Videos before: {before_count}, after: {after_count}, created: {created}"
    )


if __name__ == "__main__":
    main()
