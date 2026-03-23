"""Вкладка управления заказами (реализация IOrderView)."""

import customtkinter as ctk
from tkinter import messagebox
from view.interfaces import IOrderView
from view.dialogs import OrderDialog
from utils.constants import ORDER_STATUSES, ALL_FILTER


class OrderView(ctk.CTkFrame, IOrderView):
    """Вкладка «Заказы» — таблица, фильтры, поиск, кнопки действий."""

    def __init__(self, parent: ctk.CTkFrame):
        super().__init__(parent, fg_color="transparent")

        self._presenter = None

        self._orders: list[dict] = []
        self._available_drinks: list[dict] = []

        self._checkboxes: dict[str, ctk.BooleanVar] = {}

        self._search_var = ctk.StringVar()
        self._filter_status_var = ctk.StringVar(value=ALL_FILTER)

        self._create_widgets()

    def set_presenter(self, presenter) -> None:
        self._presenter = presenter
        self._presenter.load_orders()

    # --- Построение интерфейса ---

    def _create_widgets(self) -> None:
        self._create_toolbar()
        self._create_table_area()
        self._create_action_buttons()

    def _create_toolbar(self) -> None:
        toolbar = ctk.CTkFrame(self)
        toolbar.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(toolbar, text="Поиск по ID:").pack(side="left", padx=(10, 5))
        search_entry = ctk.CTkEntry(
            toolbar, textvariable=self._search_var, width=200,
            placeholder_text="Введите ID заказа..."
        )
        search_entry.pack(side="left", padx=(0, 15))
        self._search_var.trace_add("write", lambda *_: self._on_filters_changed())

        ctk.CTkLabel(toolbar, text="Статус:").pack(side="left", padx=(0, 5))
        status_values = [ALL_FILTER] + list(ORDER_STATUSES.values())
        ctk.CTkOptionMenu(
            toolbar, variable=self._filter_status_var,
            values=status_values, width=140,
            command=lambda *_: self._on_filters_changed()
        ).pack(side="left")

    def _create_table_area(self) -> None:
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=10, pady=(5, 0))

        self._select_all_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            header_frame, text="", variable=self._select_all_var,
            width=30, command=self._on_select_all
        ).pack(side="left", padx=(10, 5))

        columns = [
            ("ID", "created_at", 90),
            ("Дата", "created_at", 140),
            ("Напитков", "drink_count", 80),
            ("Сумма (₽)", "total_price", 100),
            ("Статус", "status", 100),
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
            btn_frame, text="+ Создать заказ", width=150,
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

    # --- Реализация IOrderView ---

    def display_orders(self, orders: list[dict]) -> None:
        self._orders = orders
        self._checkboxes.clear()
        self._select_all_var.set(False)

        for widget in self._table_frame.winfo_children():
            widget.destroy()

        if not orders:
            ctk.CTkLabel(
                self._table_frame, text="Заказы не найдены",
                text_color="gray", font=("", 14)
            ).pack(pady=30)
            return

        for order in orders:
            row = ctk.CTkFrame(self._table_frame, height=35)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)

            var = ctk.BooleanVar(value=False)
            self._checkboxes[order["id"]] = var
            ctk.CTkCheckBox(row, text="", variable=var, width=30).pack(
                side="left", padx=(10, 5)
            )

            ctk.CTkLabel(row, text=order["short_id"], width=90, anchor="w").pack(
                side="left", padx=2
            )
            ctk.CTkLabel(row, text=order["created_at"], width=140, anchor="w").pack(
                side="left", padx=2
            )
            ctk.CTkLabel(
                row, text=str(order["drink_count"]), width=80, anchor="w"
            ).pack(side="left", padx=2)
            ctk.CTkLabel(row, text=order["total_price"], width=100, anchor="w").pack(
                side="left", padx=2
            )

            status_colors = {
                "new": "#3B8ED0",
                "in_progress": "#F0A030",
                "ready": "#2FA572",
                "cancelled": "#D35B58",
            }
            status_color = status_colors.get(order["status"], "gray")
            ctk.CTkLabel(
                row, text=order["status_display"], width=100,
                anchor="w", text_color=status_color
            ).pack(side="left", padx=2)

    def display_available_drinks(self, drinks: list[dict]) -> None:
        self._available_drinks = drinks

    def get_selected_order_ids(self) -> list[str]:
        return [
            order_id for order_id, var in self._checkboxes.items() if var.get()
        ]

    def get_search_query(self) -> str:
        return self._search_var.get()

    def get_filter_status(self) -> str | None:
        value = self._filter_status_var.get()
        if value == ALL_FILTER:
            return None
        for key, display in ORDER_STATUSES.items():
            if display == value:
                return key
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
            self._presenter.load_orders()

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
        self._presenter.load_available_drinks()

        OrderDialog(
            parent=self.winfo_toplevel(),
            available_drinks=self._available_drinks,
            on_save=self._presenter.create_order,
        )

    def _on_edit_click(self) -> None:
        if not self._presenter:
            return

        selected = self.get_selected_order_ids()
        if len(selected) != 1:
            self.show_error("Выберите один заказ для редактирования")
            return

        order_data = self._presenter.get_order_by_id(selected[0])
        if not order_data:
            self.show_error("Заказ не найден")
            return

        self._presenter.load_available_drinks()

        available_ids = {d["id"] for d in self._available_drinks}
        drinks_for_dialog = list(self._available_drinks)
        for drink_info in order_data.get("drinks_info", []):
            if drink_info["id"] not in available_ids:
                drinks_for_dialog.append(drink_info)

        OrderDialog(
            parent=self.winfo_toplevel(),
            available_drinks=drinks_for_dialog,
            on_save=self._presenter.update_order,
            order_data=order_data,
        )

    def _on_delete_selected_click(self) -> None:
        if self._presenter:
            self._presenter.delete_selected()