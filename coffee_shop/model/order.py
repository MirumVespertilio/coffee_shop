"""Модель заказа."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


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
    total_price: float
    status: OrderStatus = OrderStatus.NEW
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> dict:
        """Сериализация в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "drink_ids": self.drink_ids,
            "created_at": self.created_at,
            "status": self.status.value if isinstance(self.status, OrderStatus) else self.status,
            "total_price": self.total_price,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        """Десериализация из словаря."""
        return cls(
            id=data["id"],
            drink_ids=data["drink_ids"],
            created_at=data["created_at"],
            status=OrderStatus(data["status"]),
            total_price=float(data["total_price"]),
        )