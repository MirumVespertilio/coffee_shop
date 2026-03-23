"""Модель категории напитка."""

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Category:
    """Категория напитка (Кофе, Чай и т.д.)."""

    name: str
    id: str = field(default_factory=lambda: str(uuid4()))

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