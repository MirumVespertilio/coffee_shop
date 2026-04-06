"""Модель заказа."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


class OrderValidationError(Exception):
    """Исключение при ошибке валидации заказа."""
    pass


class OrderStatus(str, Enum):
    """Статус заказа."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    CANCELLED = "cancelled"


@dataclass
class Order:
    """Заказ в кофейне."""

    drink_ids: list[str]
    _drink_prices: dict[str, float] = field(default_factory=dict)
    status: OrderStatus = OrderStatus.NEW
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        """Валидация данных при создании объекта."""
        if not self.drink_ids:
            raise OrderValidationError("Заказ должен содержать хотя бы один напиток")

    @property
    def total_price(self) -> float:
        """Вычисление суммы заказа."""
        return round(sum(self._drink_prices.values()), 2)

    def to_dict(self) -> dict:
        """Сериализация в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "drink_ids": self.drink_ids,
            "drink_prices": self._drink_prices,
            "created_at": self.created_at,
            "status": self.status.value if isinstance(self.status, OrderStatus) else self.status,
            "total_price": self.total_price,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        """Десериализация из словаря."""
        # Обратная совместимость: если drink_prices нет, берём total_price
        drink_prices = data.get("drink_prices", {})
        if not drink_prices and "total_price" in data:
            # Равномерно распределяем цену по напиткам для совместимости
            total = float(data["total_price"])
            count = len(data["drink_ids"])
            if count > 0:
                price_per_drink = total / count
                drink_prices = {did: price_per_drink for did in data["drink_ids"]}

        return cls(
            id=data["id"],
            drink_ids=data["drink_ids"],
            _drink_prices=drink_prices,
            created_at=data["created_at"],
            status=OrderStatus(data["status"]),
        )
