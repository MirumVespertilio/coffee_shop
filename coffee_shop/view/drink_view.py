"""Вкладка управления напитками (реализация IDrinkView)."""

import customtkinter as ctk
from tkinter import messagebox
from view.interfaces import IDrinkView
from view.dialogs import DrinkDialog
from utils.constants import DRINK_SIZES, ALL_FILTER


class DrinkView(ctk.CTkFrame, IDrinkView):
    """Вкладка «Напитки» — таблица, фильтры, поиск, кнопки действий."""

    def __init__(self, parent: ctk.CTkFrame):
        super().__init__(parent, fg_color="transparent")

        self._presenter = None

        self._drinks: list[dict] = []
        self._categories: list[dict] = []

        self._checkboxes: dict[str, ctk.BooleanVar] = {}

        self._search_var = ctk.StringVar()
        self._filter_category_var = ctk.StringVar(value=ALL_FILTER)
        self._filter_size_var = ctk.StringVar(value=ALL_FILTER)
        self._filter_available_var = ctk.StringVar(value=ALL_FILTER)

        self._create_widgets()

    def set_presenter(self, presenter) -> None:
        self._presenter = presenter
        self._presenter.load_categories()
        self._presenter.load_drinks()

    # --- Построение интерфейса ---

    def _create_widgets(self) -> None:
        self._create_toolbar()
        self._create_table_area()
        self._create_action_buttons()

    def _create_toolbar(self) -> None:
        toolbar = ctk.CTkFrame(self)
        toolbar.pack(fill="x", padx=10, pady=(10, 5))

        # Поиск
        ctk.CTkLabel(toolbar, text="Поиск:").pack(side="left", padx=(10, 5))
        search_entry = ctk.CTkEntry(
            toolbar, textvariable=self._search_var, width=200,
            placeholder_text="Название напитка..."
        )
        search_entry.pack(side="left", padx=(0, 15))
        self._search_var.trace_add("write", lambda *_: self._on_filters_changed())

        # Фильтр: категория
        ctk.CTkLabel(toolbar, text="Категория:").pack(side="left", padx=(0, 5))
        self._category_filter_menu = ctk.CTkOptionMenu(
            toolbar, variable=self._filter_category_var,
            values=[ALL_FILTER], width=140,
            command=lambda *_: self._on_filters_changed()
        )
        self._category_filter_menu.pack(side="left", padx=(0, 15))

        # Фильтр: размер
        ctk.CTkLabel(toolbar, text="Размер:").pack(side="left", padx=(0, 5))
        size_values = [ALL_FILTER] + list(DRINK_SIZES)
        ctk.CTkOptionMenu(
            toolbar, variable=self._filter_size_var,
            values=size_values, width=80,
            command=lambda *_: self._on_filters_changed()
        ).pack(side="left", padx=(0, 15))

        # Фильтр: доступность
        ctk.CTkLabel(toolbar, text="Наличие:").pack(side="left", padx=(0, 5))
        ctk.CTkOptionMenu(
            toolbar, variable=self._filter_available_var,
            values=[ALL_FILTER, "Да", "Нет"], width=80,
            command=lambda *_: self._on_filters_changed()
        ).pack(side="left")

    def _create_table_area(self) -> None:
        # Заголовки
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=10, pady=(5, 0))

        self._select_all_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            header_frame, text="", variable=self._select_all_var,
            width=30, command=self._on_select_all
        ).pack(side="left", padx=(10, 5))

        columns = [
            ("Название", "name", 200),
            ("Категория", "category", 130),
            ("Размер", "size", 70),
            ("Цена (₽)", "price", 90),
            ("Доступен", "available", 80),
        ]
        for text, field, width in columns:
            btn = ctk.CTkButton(
                header_frame, text=text, width=width,
                fg_color="transparent", hover_color=("gray75", "gray30"),
                text_color=("gray10", "gray90"), anchor="w",
                command=lambda f=field: self._on_sort_click(f)
            )
            btn.pack(side="left", padx=2)

        self._table_frame = ctk.CTkScrollableFrame(self, height=350)
        self._table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))

    def _create_action_buttons(self) -> None:
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkButton(
            btn_frame, text="+ Добавить", width=130,
            command=self._on_add_click
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            btn_frame, text="✎ Редактировать", width=150,
            command=self._on_edit_click
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, text="🗑 Удалить выбранные", width=170,
            fg_color="#D35B58", hover_color="#C04040",
            command=self._on_delete_selected_click
        ).pack(side="right")

    # --- Реализация IDrinkView ---

    def display_drinks(self, drinks: list[dict]) -> None:
        self._drinks = drinks
        self._checkboxes.clear()
        self._select_all_var.set(False)

        for widget in self._table_frame.winfo_children():
            widget.destroy()

        if not drinks:
            ctk.CTkLabel(
                self._table_frame, text="Напитки не найдены",
                text_color="gray", font=("", 14)
            ).pack(pady=30)
            return

        for drink in drinks:
            row = ctk.CTkFrame(self._table_frame, height=35)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)

            var = ctk.BooleanVar(value=False)
            self._checkboxes[drink["id"]] = var
            ctk.CTkCheckBox(row, text="", variable=var, width=30).pack(
                side="left", padx=(10, 5)
            )

            ctk.CTkLabel(row, text=drink["name"], width=200, anchor="w").pack(
                side="left", padx=2
            )
            ctk.CTkLabel(row, text=drink["category_name"], width=130, anchor="w").pack(
                side="left", padx=2
            )
            ctk.CTkLabel(row, text=drink["size"], width=70, anchor="w").pack(
                side="left", padx=2
            )
            ctk.CTkLabel(row, text=drink["price"], width=90, anchor="w").pack(
                side="left", padx=2
            )

            avail_text = "✓" if drink["available"] else "✗"
            avail_color = "green" if drink["available"] else "red"
            ctk.CTkLabel(
                row, text=avail_text, width=80, anchor="w", text_color=avail_color
            ).pack(side="left", padx=2)

    def display_categories(self, categories: list[dict]) -> None:
        self._categories = categories
        cat_names = [ALL_FILTER] + [c["name"] for c in categories]
        self._category_filter_menu.configure(values=cat_names)

    def get_selected_drink_ids(self) -> list[str]:
        return [
            drink_id for drink_id, var in self._checkboxes.items() if var.get()
        ]

    def get_search_query(self) -> str:
        return self._search_var.get()

    def get_filter_category(self) -> str | None:
        value = self._filter_category_var.get()
        if value == ALL_FILTER:
            return None
        for cat in self._categories:
            if cat["name"] == value:
                return cat["id"]
        return None

    def get_filter_size(self) -> str | None:
        value = self._filter_size_var.get()
        return None if value == ALL_FILTER else value

    def get_filter_available(self) -> bool | None:
        value = self._filter_available_var.get()
        if value == "Да":
            return True
        if value == "Нет":
            return False
        return None

    def show_error(self, message: str) -> None:
        messagebox.showerror("Ошибка", message)

    def show_success(self, message: str) -> None:
        messagebox.showinfo("Успех", message)

    def ask_confirmation(self, message: str) -> bool:
        return messagebox.askyesno("Подтверждение", message)

    # --- Обработчики событий ---

    def _on_filters_changed(self) -> None:
        if self._presenter:
            self._presenter.load_drinks()

    def _on_sort_click(self, field: str) -> None:
        if self._presenter:
            self._presenter.set_sort(field)

    def _on_select_all(self) -> None:
        state = self._select_all_var.get()
        for var in self._checkboxes.values():
            var.set(state)

    def _on_add_click(self) -> None:
        if not self._presenter:
            return
        DrinkDialog(
            parent=self.winfo_toplevel(),
            categories=self._categories,
            on_save=self._presenter.add_drink,
        )

    def _on_edit_click(self) -> None:
        if not self._presenter:
            return

        selected = self.get_selected_drink_ids()
        if len(selected) != 1:
            self.show_error("Выберите один напиток для редактирования")
            return

        drink_data = self._presenter.get_drink_by_id(selected[0])
        if not drink_data:
            self.show_error("Напиток не найден")
            return

        DrinkDialog(
            parent=self.winfo_toplevel(),
            categories=self._categories,
            on_save=self._presenter.update_drink,
            drink_data=drink_data,
        )

    def _on_delete_selected_click(self) -> None:
        if self._presenter:
            self._presenter.delete_selected()