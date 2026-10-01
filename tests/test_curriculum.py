import copy
import json
import re
import unittest
from types import SimpleNamespace

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.config import PROJECT_ROOT
from app.content.base_courses import BASE_COURSES
from app.content.curriculum import COURSES, CURRICULUM_VERSION
from app.content.practice_topics import PRACTICE_TOPIC_COUNT, PRACTICE_TOPIC_GROUPS
from app.database import Base
from app.models.db_models import Course, CurriculumUpdate, Lesson, LessonProgress, User
from app.services.course_service import seed_courses


class CurriculumTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        event.listen(self.engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine, autoflush=False)()
        self.templates = Environment(
            loader=FileSystemLoader(PROJECT_ROOT / "templates"),
            autoescape=select_autoescape(["html"]),
        )
        self.user = SimpleNamespace(username="learner", level="beginner", is_admin=False)
        self.request = SimpleNamespace(url=SimpleNamespace(path="/coding"))

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_new_database_has_complete_curriculum_and_repeat_is_unchanged(self):
        original_data = copy.deepcopy(COURSES)
        seed_courses(self.db)
        self.assertEqual(self.db.query(Course).count(), 12)
        self.assertEqual(self.db.query(Lesson).count(), 54)
        ids = [lesson.id for lesson in self.db.query(Lesson).order_by(Lesson.id)]
        seed_courses(self.db)
        self.assertEqual(ids, [lesson.id for lesson in self.db.query(Lesson).order_by(Lesson.id)])
        self.assertEqual(self.db.query(CurriculumUpdate).count(), 1)
        self.assertEqual(COURSES, original_data)

    def test_upgrade_preserves_existing_ids_content_custom_courses_and_progress(self):
        original_ids = {}
        for data in BASE_COURSES:
            course = Course(**{key: value for key, value in data.items() if key != "lessons"})
            self.db.add(course)
            self.db.flush()
            for lesson_data in data["lessons"]:
                lesson = Lesson(course_id=course.id, **lesson_data)
                self.db.add(lesson)
                self.db.flush()
                original_ids[lesson.title] = lesson.id
        course_id = course.id
        lesson_id = lesson.id
        course.description = "Edited by the teacher"
        lesson.theory = "Teacher's explanation"
        user = User(username="learner", email="learner@example.com", hashed_password="unused")
        self.db.add(user)
        self.db.flush()
        progress = LessonProgress(user_id=user.id, lesson_id=lesson_id, is_done=True, score=95)
        self.db.add(progress)
        custom = Course(title="Teacher's own course", order=99)
        self.db.add(custom)
        self.db.commit()
        custom_id = custom.id

        seed_courses(self.db)

        self.assertEqual(self.db.query(Course).count(), 13)
        self.assertEqual(self.db.query(Lesson).count(), 54)
        for title, existing_id in original_ids.items():
            self.assertEqual(self.db.query(Lesson).filter_by(title=title).one().id, existing_id)
        self.assertEqual(self.db.get(Course, course_id).description, "Edited by the teacher")
        self.assertEqual(self.db.get(Lesson, lesson_id).theory, "Teacher's explanation")
        self.assertEqual(self.db.get(Course, custom_id).title, "Teacher's own course")
        self.db.refresh(progress)
        self.assertEqual((progress.lesson_id, progress.is_done, progress.score), (lesson_id, True, 95))

    def test_custom_lesson_order_does_not_hide_added_lessons_from_navigation(self):
        data = BASE_COURSES[0]
        course = Course(title=data["title"], order=1)
        self.db.add(course)
        self.db.flush()
        custom = Lesson(course_id=course.id, title="Custom lesson", order=4, task="Custom task")
        self.db.add(custom)
        self.db.commit()

        seed_courses(self.db)

        self.db.refresh(custom)
        orders = [lesson.order for lesson in course.lessons]
        self.assertEqual(len(orders), 7)
        self.assertEqual(len(orders), len(set(orders)))
        self.assertEqual(custom.order, 4)

    def test_applied_update_respects_later_admin_deletion(self):
        seed_courses(self.db)
        course = self.db.query(Course).order_by(Course.order.desc()).first()
        deleted_id = course.id
        self.db.delete(course)
        self.db.commit()
        seed_courses(self.db)
        self.assertIsNone(self.db.get(Course, deleted_id))
        self.assertEqual(self.db.query(Course).count(), 11)
        self.assertIsNotNone(self.db.get(CurriculumUpdate, CURRICULUM_VERSION))

    def test_failed_update_rolls_back_content_and_version(self):
        from unittest.mock import patch

        with patch.object(self.db, "commit", side_effect=RuntimeError("Database failure")):
            with self.assertRaisesRegex(RuntimeError, "Database failure"):
                seed_courses(self.db)
        self.assertEqual(self.db.query(Course).count(), 0)
        self.assertEqual(self.db.query(Lesson).count(), 0)
        self.assertEqual(self.db.query(CurriculumUpdate).count(), 0)
        seed_courses(self.db)
        self.assertEqual(self.db.query(Lesson).count(), 54)

    def test_all_practice_topics_render_and_original_values_remain_available(self):
        html = self.templates.get_template("index.html").render(
            user=self.user, request=self.request,
            topic_groups=PRACTICE_TOPIC_GROUPS, topic_count=PRACTICE_TOPIC_COUNT
        )
        select = re.search(r'<select id="topic">(.*?)</select>', html, re.S).group(1)
        values = re.findall(r'<option value="([^"]+)">', select)
        self.assertEqual(len(values), 40)
        self.assertEqual(len(values), len(set(values)))
        self.assertEqual(select.count("<optgroup"), 7)
        self.assertTrue({"циклы for", "циклы while", "функции", "списки", "словари",
                         "классы и ООП", "файлы", "обработка ошибок"}.issubset(values))

    def test_every_lesson_renders_and_copy_to_editor_preserves_python_source(self):
        seed_courses(self.db)
        template = self.templates.get_template("lesson.html")
        for lesson in self.db.query(Lesson):
            with self.subTest(title=lesson.title):
                html = template.render(user=self.user, request=self.request,
                                       lesson=lesson, course_id=lesson.course_id,
                                       progress=None, next_lesson=None)
                serialized = re.search(r"const CODE_EXAMPLE = (.*);", html).group(1)
                self.assertEqual(json.loads(serialized), lesson.code_example)
                serialized_task = re.search(r"const LESSON_TASK = (.*);", html).group(1)
                self.assertEqual(json.loads(serialized_task), lesson.task)
                self.assertIn("<pre class=\"output-block\"", html)


if __name__ == "__main__":
    unittest.main()
