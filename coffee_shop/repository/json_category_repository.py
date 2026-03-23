"""JSON-реализация репозитория категорий."""

import json
import os

from model.category import Category
from repository.interfaces import ICategoryRepository
from utils.constants import CATEGORIES_FILE, DATA_DIR, DEFAULT_CATEGORIES


class JsonCategoryRepository(ICategoryRepository):
    """Хранение категорий в JSON-файле."""

    def __init__(self, file_path: str = CATEGORIES_FILE):
        self._file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Создаёт файл с предустановленными категориями, если его нет."""
        os.makedirs(DATA_DIR, exist_ok=True)

        if not os.path.exists(self._file_path):
            # Первый запуск — создаём категории по умолчанию
            default = [Category(name=name) for name in DEFAULT_CATEGORIES]
            self._save_all(default)

    def _load_all(self) -> list[Category]:
        """Читает все категории из файла."""
        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [Category.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError) as e:
            raise IOError(f"Ошибка чтения файла категорий: {e}")

    def _save_all(self, categories: list[Category]) -> None:
        """Перезаписывает все категории в файл."""
        data = [cat.to_dict() for cat in categories]
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_all(self) -> list[Category]:
        return self._load_all()

    def get_by_id(self, category_id: str) -> Category | None:
        categories = self._load_all()
        for cat in categories:
            if cat.id == category_id:
                return cat
        return None

    def add(self, category: Category) -> None:
        categories = self._load_all()
        categories.append(category)
        self._save_all(categories)

    def delete(self, category_id: str) -> None:
        categories = self._load_all()
        categories = [cat for cat in categories if cat.id != category_id]
        self._save_all(categories)