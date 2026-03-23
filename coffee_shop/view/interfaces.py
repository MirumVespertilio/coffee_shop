"""Абстрактные интерфейсы представлений (контракты для слоя View)."""

from abc import ABC, abstractmethod


class IDrinkView(ABC):
    """Интерфейс представления напитков."""

    @abstractmethod
    def display_drinks(self, drinks: list[dict]) -> None:
        """Отобразить список напитков в таблице.
        
        Каждый dict содержит: id, name, category_name, size, price, available.
        """
        ...

    @abstractmethod
    def display_categories(self, categories: list[dict]) -> None:
        """Отобразить список категорий (для фильтров и форм).
        
        Каждый dict содержит: id, name.
        """
        ...

    @abstractmethod
    def get_selected_drink_ids(self) -> list[str]:
        """Получить ID выделенных напитков в таблице."""
        ...

    @abstractmethod
    def get_search_query(self) -> str:
        """Получить текст из поля поиска."""
        ...

    @abstractmethod
    def get_filter_category(self) -> str | None:
        """Получить выбранную категорию фильтра. None = без фильтра."""
        ...

    @abstractmethod
    def get_filter_size(self) -> str | None:
        """Получить выбранный размер фильтра. None = без фильтра."""
        ...

    @abstractmethod
    def get_filter_available(self) -> bool | None:
        """Получить фильтр доступности. None = без фильтра."""
        ...

    @abstractmethod
    def show_error(self, message: str) -> None:
        """Показать сообщение об ошибке."""
        ...

    @abstractmethod
    def show_success(self, message: str) -> None:
        """Показать сообщение об успехе."""
        ...

    @abstractmethod
    def ask_confirmation(self, message: str) -> bool:
        """Запросить подтверждение действия. Возвращает True/False."""
        ...

    @abstractmethod
    def set_presenter(self, presenter) -> None:
        """Установить ссылку на презентер."""
        ...


class IOrderView(ABC):
    """Интерфейс представления заказов."""

    @abstractmethod
    def display_orders(self, orders: list[dict]) -> None:
        """Отобразить список заказов в таблице.
        
        Каждый dict содержит: id, short_id, created_at, drink_count,
        total_price, status, status_display.
        """
        ...

    @abstractmethod
    def display_available_drinks(self, drinks: list[dict]) -> None:
        """Отобразить доступные напитки (для формы создания заказа).
        
        Каждый dict содержит: id, name, category_name, size, price.
        """
        ...

    @abstractmethod
    def get_selected_order_ids(self) -> list[str]:
        """Получить ID выделенных заказов в таблице."""
        ...

    @abstractmethod
    def get_search_query(self) -> str:
        """Получить текст из поля поиска по ID."""
        ...

    @abstractmethod
    def get_filter_status(self) -> str | None:
        """Получить выбранный статус фильтра. None = без фильтра."""
        ...

    @abstractmethod
    def show_error(self, message: str) -> None:
        """Показать сообщение об ошибке."""
        ...

    @abstractmethod
    def show_success(self, message: str) -> None:
        """Показать сообщение об успехе."""
        ...

    @abstractmethod
    def ask_confirmation(self, message: str) -> bool:
        """Запросить подтверждение действия."""
        ...

    @abstractmethod
    def set_presenter(self, presenter) -> None:
        """Установить ссылку на презентер."""
        ...