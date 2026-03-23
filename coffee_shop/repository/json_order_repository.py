"""JSON-реализация репозитория заказов."""

import json
import os

from model.order import Order
from repository.interfaces import IOrderRepository
from utils.constants import ORDERS_FILE, DATA_DIR


class JsonOrderRepository(IOrderRepository):
    """Хранение заказов в JSON-файле."""

    def __init__(self, file_path: str = ORDERS_FILE):
        self._file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Создаёт пустой файл, если его нет."""
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(self._file_path):
            self._save_all([])

    def _load_all(self) -> list[Order]:
        """Читает все заказы из файла."""
        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [Order.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError) as e:
            raise IOError(f"Ошибка чтения файла заказов: {e}")

    def _save_all(self, orders: list[Order]) -> None:
        """Перезаписывает все заказы в файл."""
        data = [order.to_dict() for order in orders]
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_all(self) -> list[Order]:
        return self._load_all()

    def get_by_id(self, order_id: str) -> Order | None:
        orders = self._load_all()
        for order in orders:
            if order.id == order_id:
                return order
        return None

    def add(self, order: Order) -> None:
        orders = self._load_all()
        orders.append(order)
        self._save_all(orders)

    def update(self, order: Order) -> None:
        orders = self._load_all()
        orders = [order if o.id == order.id else o for o in orders]
        self._save_all(orders)

    def delete(self, order_id: str) -> None:
        orders = self._load_all()
        orders = [o for o in orders if o.id != order_id]
        self._save_all(orders)

    def delete_many(self, order_ids: list[str]) -> None:
        orders = self._load_all()
        ids_set = set(order_ids)
        orders = [o for o in orders if o.id not in ids_set]
        self._save_all(orders)