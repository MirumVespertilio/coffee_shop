"""Модель напитка."""

from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class DrinkSize(str, Enum):
    """Размер порции напитка."""
    S = "S"
    M = "M"
    L = "L"


@dataclass
class Drink:
    """Напиток в меню кофейни."""

    name: str
    category_id: str
    size: DrinkSize
    price: float
    available: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> dict:
        """Сериализация в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "category_id": self.category_id,
            "size": self.size.value if isinstance(self.size, DrinkSize) else self.size,
            "price": self.price,
            "available": self.available,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Drink":
        """Десериализация из словаря."""
        return cls(
            id=data["id"],
            name=data["name"],
            category_id=data["category_id"],
            size=DrinkSize(data["size"]),
            price=float(data["price"]),
            available=data["available"],
        )