"""
CoffeeShop Manager — точка входа.

Здесь собирается граф зависимостей (Dependency Injection):
  Repository → Presenter → View
"""

import customtkinter as ctk
from utils.constants import APPEARANCE_MODE, COLOR_THEME

# Репозитории
from repository.json_category_repository import JsonCategoryRepository
from repository.json_drink_repository import JsonDrinkRepository
from repository.json_order_repository import JsonOrderRepository

# Представления
from view.main_window import MainWindow
from view.drink_view import DrinkView
from view.order_view import OrderView

# Презентеры
from presenter.drink_presenter import DrinkPresenter
from presenter.order_presenter import OrderPresenter


def main() -> None:
    """Инициализация и запуск приложения."""

    # Настройка темы
    ctk.set_appearance_mode(APPEARANCE_MODE)
    ctk.set_default_color_theme(COLOR_THEME)

    # 1. Создаём репозитории (слой данных)
    category_repo = JsonCategoryRepository()
    drink_repo = JsonDrinkRepository()
    order_repo = JsonOrderRepository()

    # 2. Создаём главное окно
    window = MainWindow()

    # 3. Создаём View (слой представления)
    drink_view = DrinkView(window.drinks_tab)
    drink_view.pack(fill="both", expand=True)

    order_view = OrderView(window.orders_tab)
    order_view.pack(fill="both", expand=True)

    # 4. Создаём Presenter (слой бизнес-логики)
    #    Презентеры связывают View и Repository
    #    При создании презентер вызывает view.set_presenter(self),
    #    что запускает начальную загрузку данных
    DrinkPresenter(
        view=drink_view,
        drink_repo=drink_repo,
        category_repo=category_repo,
    )

    OrderPresenter(
        view=order_view,
        order_repo=order_repo,
        drink_repo=drink_repo,
        category_repo=category_repo,
    )

    # 5. Запуск главного цикла
    window.mainloop()


if __name__ == "__main__":
    main()