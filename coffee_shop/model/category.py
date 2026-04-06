"""Модель категории напитка."""

from dataclasses import dataclass, field
from uuid import uuid4

# Константы валидации
MAX_CATEGORY_NAME_LENGTH = 50


class CategoryValidationError(Exception):
    """Исключение при ошибке валидации категории."""
    pass


@dataclass
class Category:
    """Категория напитка (Кофе, Чай и т.д.)."""

    name: str
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        """Валидация данных при создании объекта"""
        if not self.name or not self.name.strip():
            raise CategoryValidationError("Название категории не может быть пустым")
        if len(self.name.strip()) > MAX_CATEGORY_NAME_LENGTH:
            raise CategoryValidationError(f"Название слишком длинное (макс. {MAX_CATEGORY_NAME_LENGTH})")

    def to_dict(self) -> dict:
        """Сериализация в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Category":
        """Десериализация из словаря."""
        return cls(
            id=data["id"],
            name=data["name"],
        )
