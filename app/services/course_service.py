from sqlalchemy.orm import Session

from app.content.curriculum import COURSES, CURRICULUM_VERSION
from app.models.db_models import Course, CurriculumUpdate, Lesson


def seed_courses(db: Session):
    """Add a curriculum update once, keeping existing content and progress."""
    if db.get(CurriculumUpdate, CURRICULUM_VERSION) is not None:
        return

    try:
        for course_data in COURSES:
            course = db.query(Course).filter_by(title=course_data["title"]).first()
            if course is None:
                course = Course(**{
                    key: value for key, value in course_data.items() if key != "lessons"
                })
                db.add(course)
                db.flush()

            existing_titles = {lesson.title for lesson in course.lessons}
            existing_orders = {lesson.order for lesson in course.lessons}
            for lesson_data in course_data["lessons"]:
                if lesson_data["title"] in existing_titles:
                    continue
                # Keep custom lessons in place if their order is already occupied.
                order = lesson_data["order"]
                if order in existing_orders:
                    order = max(existing_orders, default=0) + 1
                lesson = Lesson(course_id=course.id, **{**lesson_data, "order": order})
                db.add(lesson)
                existing_titles.add(lesson.title)
                existing_orders.add(order)

        db.add(CurriculumUpdate(version=CURRICULUM_VERSION))
        db.commit()
    except Exception:
        db.rollback()
        raise
