"""Презентер для управления напитками."""

from model.drink import Drink, DrinkSize, DrinkValidationError
from model.category import Category, CategoryValidationError
from repository.interfaces import ICategoryRepository, IDrinkRepository
from view.interfaces import IDrinkView


class DrinkPresenter:
    """Связывает IDrinkView с репозиториями. Координирует действия между слоями."""

    def __init__(
        self,
        view: IDrinkView,
        drink_repo: IDrinkRepository,
        category_repo: ICategoryRepository,
    ):
        self._view = view
        self._drink_repo = drink_repo
        self._category_repo = category_repo

        self._sort_field: str = "name"
        self._sort_ascending: bool = True

        self._view.set_presenter(self)

    # --- Загрузка данных ---

    def load_drinks(self) -> None:
        """Загружает напитки с учётом фильтров, поиска и сортировки."""
        try:
            drinks = self._drink_repo.get_all()
            categories = self._category_repo.get_all()
            cat_map = {cat.id: cat.name for cat in categories}

            drinks = self._apply_filters(drinks)
            drinks = self._apply_search(drinks)
            drinks = self._apply_sort(drinks, cat_map)

            drink_dicts = [
                {
                    "id": d.id,
                    "name": d.name,
                    "category_name": cat_map.get(d.category_id, "—"),
                    "size": d.size.value,
                    "price": f"{d.price:.2f}",
                    "available": d.available,
                }
                for d in drinks
            ]

            self._view.display_drinks(drink_dicts)

        except IOError as e:
            self._view.show_error(str(e))

    def load_categories(self) -> None:
        """Загружает категории для фильтров и формы создания."""
        try:
            categories = self._category_repo.get_all()
            cat_dicts = [{"id": c.id, "name": c.name} for c in categories]
            self._view.display_categories(cat_dicts)
        except IOError as e:
            self._view.show_error(str(e))

    # --- CRUD операции ---

    def add_drink(
        self, name: str, category_id: str, size: str, price_str: str, available: bool
    ) -> bool:
        """Добавить напиток. Возвращает True при успехе."""
        # Базовая проверка на пустоту категории (UI-валидация)
        if not category_id:
            self._view.show_error("Выберите категорию")
            return False

        # Преобразование цены (логика представления)
        try:
            price = round(float(price_str.strip()), 2)
        except ValueError:
            self._view.show_error("Цена должна быть числом")
            return False

        try:
            # Создание напитка
            drink = Drink(
                name=name.strip(),
                category_id=category_id,
                size=DrinkSize(size),
                price=price,
                available=available,
            )
            self._drink_repo.add(drink)
            self.load_drinks()
            self._view.show_success(f"Напиток «{drink.name}» добавлен")
            return True
        except DrinkValidationError as e:
            # Ошибка валидации модели
            self._view.show_error(str(e))
            return False
        except IOError as e:
            self._view.show_error(str(e))
            return False

    def update_drink(
        self,
        drink_id: str,
        name: str,
        category_id: str,
        size: str,
        price_str: str,
        available: bool,
    ) -> bool:
        """Обновить напиток. Возвращает True при успехе."""
        # Базовая проверка на пустоту категории (UI-валидация)
        if not category_id:
            self._view.show_error("Выберите категорию")
            return False

        # Преобразование цены (логика представления)
        try:
            price = round(float(price_str.strip()), 2)
        except ValueError:
            self._view.show_error("Цена должна быть числом")
            return False

        try:
            # Создание напитка
            drink = Drink(
                id=drink_id,
                name=name.strip(),
                category_id=category_id,
                size=DrinkSize(size),
                price=price,
                available=available,
            )
            self._drink_repo.update(drink)
            self.load_drinks()
            self._view.show_success(f"Напиток «{drink.name}» обновлён")
            return True
        except DrinkValidationError as e:
            # Ошибка валидации модели
            self._view.show_error(str(e))
            return False
        except IOError as e:
            self._view.show_error(str(e))
            return False

    def delete_selected(self) -> None:
        """Удалить выбранные напитки."""
        selected_ids = self._view.get_selected_drink_ids()
        if not selected_ids:
            self._view.show_error("Выберите напитки для удаления")
            return

        count = len(selected_ids)
        word = self._pluralize(count, "напиток", "напитка", "напитков")
        if not self._view.ask_confirmation(f"Удалить {count} {word}?"):
            return

        try:
            self._drink_repo.delete_many(selected_ids)
            self.load_drinks()
            self._view.show_success(f"Удалено: {count} {word}")
        except IOError as e:
            self._view.show_error(str(e))

    # --- Категории ---

    def add_category(self, name: str) -> bool:
        """Добавить новую категорию. Возвращает True при успехе."""
        # Проверка уникальности
        try:
            existing = self._category_repo.get_all()
            existing_names = [c.name.lower() for c in existing]
            if name.strip().lower() in existing_names:
                self._view.show_error("Такая категория уже существует")
                return False

            # Создание категории
            category = Category(name=name.strip())
            self._category_repo.add(category)
            self.load_categories()
            return True
        except CategoryValidationError as e:
            # Ошибка валидации модели
            self._view.show_error(str(e))
            return False
        except IOError as e:
            self._view.show_error(str(e))
            return False

    def delete_category(self, category_id: str) -> bool:
        """Удалить категорию, если нет связанных напитков."""
        try:
            drinks = self._drink_repo.get_all()
            linked = [d for d in drinks if d.category_id == category_id]

            if linked:
                self._view.show_error(
                    f"Нельзя удалить: {len(linked)} напитков используют эту категорию"
                )
                return False

            category = self._category_repo.get_by_id(category_id)
            if not category:
                self._view.show_error("Категория не найдена")
                return False

            if not self._view.ask_confirmation(
                f"Удалить категорию «{category.name}»?"
            ):
                return False

            self._category_repo.delete(category_id)
            self.load_categories()
            self.load_drinks()
            self._view.show_success("Категория удалена")
            return True
        except IOError as e:
            self._view.show_error(str(e))
            return False

    # --- Сортировка ---

    def set_sort(self, field: str) -> None:
        """Изменить поле сортировки."""
        if self._sort_field == field:
            self._sort_ascending = not self._sort_ascending
        else:
            self._sort_field = field
            self._sort_ascending = True
        self.load_drinks()

    # --- Получение данных для диалогов ---

    def get_drink_by_id(self, drink_id: str) -> dict | None:
        """Получить данные напитка для формы редактирования."""
        try:
            drink = self._drink_repo.get_by_id(drink_id)
            if not drink:
                return None
            return {
                "id": drink.id,
                "name": drink.name,
                "category_id": drink.category_id,
                "size": drink.size.value,
                "price": str(drink.price),
                "available": drink.available,
            }
        except IOError:
            return None

    # --- Приватные методы (логика представления) ---

    def _apply_filters(self, drinks: list[Drink]) -> list[Drink]:
        cat_filter = self._view.get_filter_category()
        if cat_filter:
            drinks = [d for d in drinks if d.category_id == cat_filter]

        size_filter = self._view.get_filter_size()
        if size_filter:
            drinks = [d for d in drinks if d.size.value == size_filter]

        avail_filter = self._view.get_filter_available()
        if avail_filter is not None:
            drinks = [d for d in drinks if d.available == avail_filter]

        return drinks

    def _apply_search(self, drinks: list[Drink]) -> list[Drink]:
        query = self._view.get_search_query().strip().lower()
        if not query:
            return drinks
        return [d for d in drinks if query in d.name.lower()]

    def _apply_sort(
        self, drinks: list[Drink], cat_map: dict[str, str]
    ) -> list[Drink]:
        key_funcs = {
            "name": lambda d: d.name.lower(),
            "category": lambda d: cat_map.get(d.category_id, "").lower(),
            "size": lambda d: ["S", "M", "L"].index(d.size.value),
            "price": lambda d: d.price,
            "available": lambda d: d.available,
        }
        key_func = key_funcs.get(self._sort_field, key_funcs["name"])
        return sorted(drinks, key=key_func, reverse=not self._sort_ascending)

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
