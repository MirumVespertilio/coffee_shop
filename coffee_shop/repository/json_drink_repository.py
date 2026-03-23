"""JSON-реализация репозитория напитков."""

import json
import os

from model.drink import Drink
from repository.interfaces import IDrinkRepository
from utils.constants import DRINKS_FILE, DATA_DIR


class JsonDrinkRepository(IDrinkRepository):
    """Хранение напитков в JSON-файле."""

    def __init__(self, file_path: str = DRINKS_FILE):
        self._file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Создаёт пустой файл, если его нет."""
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(self._file_path):
            self._save_all([])

    def _load_all(self) -> list[Drink]:
        """Читает все напитки из файла."""
        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [Drink.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError) as e:
            raise IOError(f"Ошибка чтения файла напитков: {e}")

    def _save_all(self, drinks: list[Drink]) -> None:
        """Перезаписывает все напитки в файл."""
        data = [drink.to_dict() for drink in drinks]
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_all(self) -> list[Drink]:
        return self._load_all()

    def get_by_id(self, drink_id: str) -> Drink | None:
        drinks = self._load_all()
        for drink in drinks:
            if drink.id == drink_id:
                return drink
        return None

    def add(self, drink: Drink) -> None:
        drinks = self._load_all()
        drinks.append(drink)
        self._save_all(drinks)

    def update(self, drink: Drink) -> None:
        drinks = self._load_all()
        # Заменяем напиток с совпадающим id
        drinks = [drink if d.id == drink.id else d for d in drinks]
        self._save_all(drinks)

    def delete(self, drink_id: str) -> None:
        drinks = self._load_all()
        drinks = [d for d in drinks if d.id != drink_id]
        self._save_all(drinks)

    def delete_many(self, drink_ids: list[str]) -> None:
        drinks = self._load_all()
        ids_set = set(drink_ids)  # для быстрого поиска O(1)
        drinks = [d for d in drinks if d.id not in ids_set]
        self._save_all(drinks)