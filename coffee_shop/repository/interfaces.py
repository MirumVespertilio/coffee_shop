"""Абстрактные интерфейсы репозиториев (контракты для слоя данных)."""

from abc import ABC, abstractmethod
from model.category import Category
from model.drink import Drink
from model.order import Order


class ICategoryRepository(ABC):
    """Интерфейс репозитория категорий."""

    @abstractmethod
    def get_all(self) -> list[Category]:
        """Получить все категории."""
        ...

    @abstractmethod
    def get_by_id(self, category_id: str) -> Category | None:
        """Получить категорию по ID. Возвращает None, если не найдена."""
        ...

    @abstractmethod
    def add(self, category: Category) -> None:
        """Добавить новую категорию."""
        ...

    @abstractmethod
    def delete(self, category_id: str) -> None:
        """Удалить категорию по ID."""
        ...


class IDrinkRepository(ABC):
    """Интерфейс репозитория напитков."""

    @abstractmethod
    def get_all(self) -> list[Drink]:
        """Получить все напитки."""
        ...

    @abstractmethod
    def get_by_id(self, drink_id: str) -> Drink | None:
        """Получить напиток по ID."""
        ...

    @abstractmethod
    def add(self, drink: Drink) -> None:
        """Добавить новый напиток."""
        ...

    @abstractmethod
    def update(self, drink: Drink) -> None:
        """Обновить существующий напиток."""
        ...

    @abstractmethod
    def delete(self, drink_id: str) -> None:
        """Удалить напиток по ID."""
        ...

    @abstractmethod
    def delete_many(self, drink_ids: list[str]) -> None:
        """Удалить несколько напитков по списку ID."""
        ...


class IOrderRepository(ABC):
    """Интерфейс репозитория заказов."""

    @abstractmethod
    def get_all(self) -> list[Order]:
        """Получить все заказы."""
        ...

    @abstractmethod
    def get_by_id(self, order_id: str) -> Order | None:
        """Получить заказ по ID."""
        ...

    @abstractmethod
    def add(self, order: Order) -> None:
        """Добавить новый заказ."""
        ...

    @abstractmethod
    def update(self, order: Order) -> None:
        """Обновить существующий заказ."""
        ...

    @abstractmethod
    def delete(self, order_id: str) -> None:
        """Удалить заказ по ID."""
        ...

    @abstractmethod
    def delete_many(self, order_ids: list[str]) -> None:
        """Удалить несколько заказов по списку ID."""
        ...