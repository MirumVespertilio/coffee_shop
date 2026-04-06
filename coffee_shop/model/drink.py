"""Модель напитка."""

from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

# Константы валидации
MAX_DRINK_NAME_LENGTH = 100
MAX_PRICE = 99999.99
MIN_PRICE = 0.01
DRINK_SIZES = ("S", "M", "L")


class DrinkValidationError(Exception):
    """Исключение при ошибке валидации напитка."""
    pass


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

    def __post_init__(self):
        """Валидация данных при создании объекта (бизнес-логика модели)."""
        # Валидация названия
        if not self.name or not self.name.strip():
            raise DrinkValidationError("Название не может быть пустым")
        if len(self.name.strip()) > MAX_DRINK_NAME_LENGTH:
            raise DrinkValidationError(f"Название слишком длинное (макс. {MAX_DRINK_NAME_LENGTH})")

        # Валидация размера
        if self.size not in DRINK_SIZES:
            raise DrinkValidationError("Некорректный размер напитка")

        # Валидация цены
        if self.price < MIN_PRICE:
            raise DrinkValidationError(f"Цена должна быть не менее {MIN_PRICE}")
        if self.price > MAX_PRICE:
            raise DrinkValidationError(f"Цена не может превышать {MAX_PRICE}")

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