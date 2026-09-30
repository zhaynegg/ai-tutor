from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        conn.execute(text("DELETE FROM lesson_progress"))
        conn.execute(text("DELETE FROM lessons"))
        conn.execute(text("DELETE FROM courses"))
        conn.commit()
        print("OK: курсы, уроки и прогресс удалены")
    except Exception as e:
        print("Ошибка:", e)