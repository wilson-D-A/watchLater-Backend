from sqlalchemy.orm import Session

from crud import get_all_tags_in_category
from database import engine

# def seed_videos(session: Session):
#     with Session(engine) as session:
#         before_count = session.scalar(select(func.count(Video.id))) or 0
#         seed_videos_from_file(session)
#         after_count = session.scalar(select(func.count(Video.id))) or 0

#     created = after_count - before_count
#     print(
#         f"Seed completed. Videos before: {before_count}, after: {after_count}, created: {created}"
#     )


def main() -> None:
    with Session(engine) as session:
        category = "Frontend"
        tags = get_all_tags_in_category(session, category)
        print(f"Tags in category '{category}':")
        for tag in tags:
            print(tag)


if __name__ == "__main__":
    main()
