"""Главное окно приложения с вкладками."""

import customtkinter as ctk
from utils.constants import WINDOW_TITLE, WINDOW_SIZE, WINDOW_MIN_SIZE


class MainWindow(ctk.CTk):
    """Главное окно CoffeeShop Manager."""

    def __init__(self):
        super().__init__()

        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        self.minsize(*WINDOW_MIN_SIZE)

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Создание вкладок."""
        self._tabview = ctk.CTkTabview(self)
        self._tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Создаём вкладки
        self._drinks_tab = self._tabview.add("☕ Напитки")
        self._orders_tab = self._tabview.add("📋 Заказы")

    @property
    def drinks_tab(self) -> ctk.CTkFrame:
        """Фрейм вкладки напитков."""
        return self._drinks_tab

    @property
    def orders_tab(self) -> ctk.CTkFrame:
        """Фрейм вкладки заказов."""
        return self._orders_tab