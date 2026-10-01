"""The complete built-in learning path, from Python basics to projects."""

from app.content.base_courses import BASE_COURSES
from app.content.course_extensions import COURSE_EXTENSIONS
from app.content.core_courses import CORE_COURSES
from app.content.advanced_courses import ADVANCED_COURSES


COURSES = [
    {
        **course,
        "difficulty": "beginner",
        "lessons": [*course["lessons"], *COURSE_EXTENSIONS[course["title"]]],
    }
    for course in BASE_COURSES
] + CORE_COURSES + ADVANCED_COURSES

# Each version is applied once, so later admin edits and deletions are respected.
CURRICULUM_VERSION = "expanded_python_curriculum_v1"
