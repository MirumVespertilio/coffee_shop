"""Презентер для управления заказами."""

from model.order import Order, OrderStatus, OrderValidationError
from repository.interfaces import IDrinkRepository, IOrderRepository, ICategoryRepository
from view.interfaces import IOrderView
from utils.constants import ORDER_STATUSES


class OrderPresenter:
    """Связывает IOrderView с репозиториями. Координирует действия между слоями."""

    def __init__(
        self,
        view: IOrderView,
        order_repo: IOrderRepository,
        drink_repo: IDrinkRepository,
        category_repo: ICategoryRepository,
    ):
        self._view = view
        self._order_repo = order_repo
        self._drink_repo = drink_repo
        self._category_repo = category_repo

        self._sort_field: str = "created_at"
        self._sort_ascending: bool = False

        self._view.set_presenter(self)

    # --- Загрузка данных ---

    def load_orders(self) -> None:
        """Загружает заказы с учётом фильтров, поиска и сортировки."""
        try:
            orders = self._order_repo.get_all()
            orders = self._apply_filters(orders)
            orders = self._apply_search(orders)
            orders = self._apply_sort(orders)

            order_dicts = [
                {
                    "id": o.id,
                    "short_id": o.id[:8] + "...",
                    "created_at": o.created_at[:16].replace("T", " "),
                    "drink_count": len(o.drink_ids),
                    "total_price": f"{o.total_price:.2f}",
                    "status": o.status.value,
                    "status_display": ORDER_STATUSES.get(
                        o.status.value
                        if isinstance(o.status, OrderStatus)
                        else o.status,
                        o.status.value,
                    ),
                }
                for o in orders
            ]

            self._view.display_orders(order_dicts)

        except IOError as e:
            self._view.show_error(str(e))

    def load_available_drinks(self) -> None:
        """Загружает доступные напитки для формы создания заказа."""
        try:
            drinks = self._drink_repo.get_all()
            categories = self._category_repo.get_all()
            cat_map = {c.id: c.name for c in categories}

            available = [d for d in drinks if d.available]

            drink_dicts = [
                {
                    "id": d.id,
                    "name": d.name,
                    "category_name": cat_map.get(d.category_id, "—"),
                    "size": d.size.value,
                    "price": f"{d.price:.2f}",
                }
                for d in available
            ]

            self._view.display_available_drinks(drink_dicts)

        except IOError as e:
            self._view.show_error(str(e))

    # --- CRUD операции ---

    def create_order(self, drink_ids: list[str]) -> bool:
        """Создать новый заказ. Возвращает True при успехе."""
        try:
            # Сбор цен напитков (координация данных)
            drink_prices: dict[str, float] = {}
            for did in drink_ids:
                drink = self._drink_repo.get_by_id(did)
                if not drink:
                    self._view.show_error(f"Напиток с ID {did[:8]}... не найден")
                    return False
                if not drink.available:
                    self._view.show_error(f"Напиток «{drink.name}» недоступен")
                    return False
                drink_prices[did] = drink.price

            # Создание заказа — валидация и расчёт суммы происходят в модели 
            order = Order(
                drink_ids=drink_ids,
                _drink_prices=drink_prices,
            )
            self._order_repo.add(order)
            self.load_orders()
            self._view.show_success("Заказ создан")
            return True

        except OrderValidationError as e:
            # Ошибка валидации модели
            self._view.show_error(str(e))
            return False
        except IOError as e:
            self._view.show_error(str(e))
            return False

    def update_order(
        self, order_id: str, drink_ids: list[str], status: str
    ) -> bool:
        """Обновить заказ. Возвращает True при успехе."""
        try:
            # Преобразование статуса
            try:
                new_status = OrderStatus(status)
            except ValueError:
                self._view.show_error("Некорректный статус заказа")
                return False

            # Сбор цен напитков
            drink_prices: dict[str, float] = {}
            for did in drink_ids:
                drink = self._drink_repo.get_by_id(did)
                if not drink:
                    self._view.show_error(f"Напиток с ID {did[:8]}... не найден")
                    return False
                drink_prices[did] = drink.price

            existing = self._order_repo.get_by_id(order_id)
            if not existing:
                self._view.show_error("Заказ не найден")
                return False

            # Создание заказа — валидация и расчёт суммы происходят в модели
            updated_order = Order(
                id=order_id,
                drink_ids=drink_ids,
                _drink_prices=drink_prices,
                created_at=existing.created_at,
                status=new_status,
            )
            self._order_repo.update(updated_order)
            self.load_orders()
            self._view.show_success("Заказ обновлён")
            return True

        except OrderValidationError as e:
            # Ошибка валидации модели
            self._view.show_error(str(e))
            return False
        except IOError as e:
            self._view.show_error(str(e))
            return False

    def delete_selected(self) -> None:
        """Удалить выбранные заказы."""
        selected_ids = self._view.get_selected_order_ids()
        if not selected_ids:
            self._view.show_error("Выберите заказы для удаления")
            return

        count = len(selected_ids)
        word = self._pluralize(count, "заказ", "заказа", "заказов")
        if not self._view.ask_confirmation(f"Удалить {count} {word}?"):
            return

        try:
            self._order_repo.delete_many(selected_ids)
            self.load_orders()
            self._view.show_success(f"Удалено: {count} {word}")
        except IOError as e:
            self._view.show_error(str(e))

    # --- Сортировка ---

    def set_sort(self, field: str) -> None:
        if self._sort_field == field:
            self._sort_ascending = not self._sort_ascending
        else:
            self._sort_field = field
            self._sort_ascending = True
        self.load_orders()

    # --- Получение данных для диалогов ---

    def get_order_by_id(self, order_id: str) -> dict | None:
        """Получить данные заказа для формы редактирования."""
        try:
            order = self._order_repo.get_by_id(order_id)
            if not order:
                return None

            drinks_info = []
            categories = self._category_repo.get_all()
            cat_map = {c.id: c.name for c in categories}

            for did in order.drink_ids:
                drink = self._drink_repo.get_by_id(did)
                if drink:
                    drinks_info.append({
                        "id": drink.id,
                        "name": drink.name,
                        "category_name": cat_map.get(drink.category_id, "—"),
                        "size": drink.size.value,
                        "price": f"{drink.price:.2f}",
                    })

            return {
                "id": order.id,
                "drink_ids": order.drink_ids,
                "drinks_info": drinks_info,
                "created_at": order.created_at,
                "status": order.status.value,
                "total_price": str(order.total_price),
            }
        except IOError:
            return None

    # --- Приватные методы ---

    def _apply_filters(self, orders: list[Order]) -> list[Order]:
        status_filter = self._view.get_filter_status()
        if status_filter:
            orders = [
                o for o in orders
                if (o.status.value if isinstance(o.status, OrderStatus) else o.status)
                == status_filter
            ]
        return orders

    def _apply_search(self, orders: list[Order]) -> list[Order]:
        query = self._view.get_search_query().strip().lower()
        if not query:
            return orders
        return [o for o in orders if query in o.id.lower()]

    def _apply_sort(self, orders: list[Order]) -> list[Order]:
        key_funcs = {
            "created_at": lambda o: o.created_at,
            "total_price": lambda o: o.total_price,
            "status": lambda o: o.status.value if isinstance(o.status, OrderStatus) else o.status,
            "drink_count": lambda o: len(o.drink_ids),
        }
        key_func = key_funcs.get(self._sort_field, key_funcs["created_at"])
        return sorted(orders, key=key_func, reverse=not self._sort_ascending)

    @staticmethod
    def _pluralize(count: int, one: str, few: str, many: str) -> str:
        n = abs(count) % 100
        if 11 <= n <= 19:
            return many
        last = n % 10
        if last == 1:
            return one
        if 2 <= last <= 4:
            return few
        return many
