import subprocess
import sys
import tempfile
import os
from app.config import settings


class CodeRunner:
    """Запускает код студента в изолированном процессе с таймаутом."""

    TIMEOUT = 5  # секунд максимум

    def run(self, code: str) -> tuple[bool, str, str]:
        """Возвращает (успех, вывод, ошибка)."""

        if not settings.ENABLE_CODE_EXECUTION:
            return False, "", "Выполнение кода отключено. Используйте AI-проверку или запускайте код локально."

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py',
            delete=False, encoding='utf-8'
        ) as f:
            f.write(code)
            tmp_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=self.TIMEOUT,
                encoding='utf-8'
            )
            success = result.returncode == 0
            return success, result.stdout.strip(), result.stderr.strip()

        except subprocess.TimeoutExpired:
            return False, "", "Превышено время выполнения (5 сек). Проверь на бесконечный цикл."

        except Exception as e:
            return False, "", f"Ошибка запуска: {str(e)}"

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


code_runner = CodeRunner()