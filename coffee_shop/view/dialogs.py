"""Диалоговые окна для создания и редактирования объектов."""

from typing import Callable, Any
import tkinter as tk
import customtkinter as ctk
from utils.constants import DRINK_SIZES, ORDER_STATUSES

# Общий тип для родительского окна
ParentWindow = ctk.CTk | ctk.CTkToplevel | tk.Tk | tk.Toplevel


class DrinkDialog(ctk.CTkToplevel):
    """Диалог создания/редактирования напитка."""

    def __init__(
        self,
        parent: ParentWindow,
        categories: list[dict],
        on_save: Callable[..., bool],
        drink_data: dict | None = None,
    ):
        super().__init__(parent)

        self._categories = categories
        self._on_save = on_save
        self._drink_data: dict = drink_data if drink_data is not None else {}
        self._is_edit = drink_data is not None
        self._parent_ref = parent

        self._cat_name_to_id: dict[str, str] = {c["name"]: c["id"] for c in categories}
        self._cat_id_to_name: dict[str, str] = {c["id"]: c["name"] for c in categories}

        self._setup_window()
        self._create_widgets()

        if self._is_edit:
            self._fill_fields()

    def _setup_window(self) -> None:
        title = "Редактировать напиток" if self._is_edit else "Добавить напиток"
        self.title(title)
        self.geometry("400x420")
        self.resizable(False, False)
        self.grab_set()

        self.update_idletasks()
        px = self._parent_ref.winfo_x()
        py = self._parent_ref.winfo_y()
        pw = self._parent_ref.winfo_width()
        ph = self._parent_ref.winfo_height()
        x = px + (pw - 400) // 2
        y = py + (ph - 420) // 2
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self) -> None:
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Название ---
        ctk.CTkLabel(main_frame, text="Название:").pack(anchor="w", pady=(0, 2))
        self._name_entry = ctk.CTkEntry(main_frame, width=350)
        self._name_entry.pack(fill="x", pady=(0, 10))

        # --- Категория ---
        ctk.CTkLabel(main_frame, text="Категория:").pack(anchor="w", pady=(0, 2))
        cat_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        cat_frame.pack(fill="x", pady=(0, 10))

        cat_names = [c["name"] for c in self._categories]
        default_cat = cat_names[0] if cat_names else ""
        self._category_var = ctk.StringVar(value=default_cat)
        self._category_menu = ctk.CTkOptionMenu(
            cat_frame, variable=self._category_var, values=cat_names, width=250
        )
        self._category_menu.pack(side="left")

        self._add_cat_btn = ctk.CTkButton(
            cat_frame, text="+ Новая", width=90, command=self._on_add_category
        )
        self._add_cat_btn.pack(side="left", padx=(10, 0))

        # --- Размер ---
        ctk.CTkLabel(main_frame, text="Размер:").pack(anchor="w", pady=(0, 2))
        self._size_var = ctk.StringVar(value=DRINK_SIZES[1])
        self._size_menu = ctk.CTkOptionMenu(
            main_frame,
            variable=self._size_var,
            values=list(DRINK_SIZES),
            width=350,
        )
        self._size_menu.pack(fill="x", pady=(0, 10))

        # --- Цена ---
        ctk.CTkLabel(main_frame, text="Цена (₽):").pack(anchor="w", pady=(0, 2))
        self._price_entry = ctk.CTkEntry(main_frame, width=350)
        self._price_entry.pack(fill="x", pady=(0, 10))

        # --- Доступность ---
        self._available_var = ctk.BooleanVar(value=True)
        self._available_check = ctk.CTkCheckBox(
            main_frame, text="Доступен для заказа", variable=self._available_var
        )
        self._available_check.pack(anchor="w", pady=(0, 10))

        # --- Ошибка ---
        self._error_label = ctk.CTkLabel(
            main_frame, text="", text_color="red", wraplength=350
        )
        self._error_label.pack(fill="x", pady=(0, 10))

        # --- Кнопки ---
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(btn_frame, text="Сохранить", command=self._on_save_click).pack(
            side="left", expand=True, padx=(0, 5)
        )
        ctk.CTkButton(
            btn_frame, text="Отмена", fg_color="gray", command=self.destroy
        ).pack(side="left", expand=True, padx=(5, 0))

    def _fill_fields(self) -> None:
        self._name_entry.insert(0, self._drink_data.get("name", ""))
        cat_name = self._cat_id_to_name.get(
            self._drink_data.get("category_id", ""), ""
        )
        self._category_var.set(cat_name)
        self._size_var.set(self._drink_data.get("size", "M"))
        self._price_entry.insert(0, self._drink_data.get("price", ""))
        self._available_var.set(self._drink_data.get("available", True))

    def _on_save_click(self) -> None:
        self._error_label.configure(text="")

        name = self._name_entry.get()
        cat_name = self._category_var.get()
        category_id = self._cat_name_to_id.get(cat_name, "")
        size = self._size_var.get()
        price = self._price_entry.get()
        available = self._available_var.get()

        if self._is_edit:
            drink_id = self._drink_data.get("id", "")
            success = self._on_save(
                drink_id, name, category_id, size, price, available
            )
        else:
            success = self._on_save(name, category_id, size, price, available)

        if success:
            self.destroy()

    def _on_add_category(self) -> None:
        CategoryDialog(self, self._parent_ref, self._on_category_added)

    def _on_category_added(self, new_cat: dict) -> None:
        self._categories.append(new_cat)
        self._cat_name_to_id[new_cat["name"]] = new_cat["id"]
        self._cat_id_to_name[new_cat["id"]] = new_cat["name"]

        cat_names = [c["name"] for c in self._categories]
        self._category_menu.configure(values=cat_names)
        self._category_var.set(new_cat["name"])

    def show_error(self, message: str) -> None:
        self._error_label.configure(text=message)


class CategoryDialog(ctk.CTkToplevel):
    """Мини-диалог для добавления новой категории."""

    def __init__(
        self,
        parent: "DrinkDialog",
        view_ref: ParentWindow,
        on_save: Callable[[dict], None],
    ):
        super().__init__(parent)

        self._on_save = on_save
        self._view_ref = view_ref

        self.title("Новая категория")
        self.geometry("300x150")
        self.resizable(False, False)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 300) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 150) // 2
        self.geometry(f"+{x}+{y}")

        self._create_widgets()

    def _create_widgets(self) -> None:
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Название категории:").pack(anchor="w", pady=(0, 5))
        self._name_entry = ctk.CTkEntry(frame, width=260)
        self._name_entry.pack(fill="x", pady=(0, 10))

        self._error_label = ctk.CTkLabel(frame, text="", text_color="red")
        self._error_label.pack(fill="x", pady=(0, 5))

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(btn_frame, text="Добавить", command=self._on_add).pack(
            side="left", expand=True, padx=(0, 5)
        )
        ctk.CTkButton(
            btn_frame, text="Отмена", fg_color="gray", command=self.destroy
        ).pack(side="left", expand=True, padx=(5, 0))

    def _on_add(self) -> None:
        name = self._name_entry.get().strip()
        if not name:
            self._error_label.configure(text="Введите название")
            return

        if hasattr(self._view_ref, "_presenter"):
            presenter = getattr(self._view_ref, "_presenter")
            success = presenter.add_category(name)
            if success:
                categories = presenter._category_repo.get_all()
                new_cat: dict | None = None
                for cat in categories:
                    if cat.name == name:
                        new_cat = {"id": cat.id, "name": cat.name}
                        break
                if new_cat is not None:
                    self._on_save(new_cat)
                self.destroy()
        else:
            self._error_label.configure(text="Ошибка: презентер недоступен")


class OrderDialog(ctk.CTkToplevel):
    """Диалог создания/редактирования заказа."""

    def __init__(
        self,
        parent: ParentWindow,
        available_drinks: list[dict],
        on_save: Callable[..., bool],
        order_data: dict | None = None,
    ):
        super().__init__(parent)

        self._available_drinks = available_drinks
        self._on_save = on_save
        self._order_data: dict = order_data if order_data is not None else {}
        self._is_edit = order_data is not None
        self._parent_ref = parent

        self._drink_vars: dict[str, ctk.BooleanVar] = {}

        self._setup_window()
        self._create_widgets()

        if self._is_edit:
            self._fill_fields()

    def _setup_window(self) -> None:
        title = "Редактировать заказ" if self._is_edit else "Создать заказ"
        self.title(title)
        self.geometry("500x550")
        self.resizable(False, False)
        self.grab_set()

        self.update_idletasks()
        px = self._parent_ref.winfo_x()
        py = self._parent_ref.winfo_y()
        pw = self._parent_ref.winfo_width()
        ph = self._parent_ref.winfo_height()
        x = px + (pw - 500) // 2
        y = py + (ph - 550) // 2
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self) -> None:
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Статус (только при редактировании) ---
        if self._is_edit:
            ctk.CTkLabel(main_frame, text="Статус:").pack(anchor="w", pady=(0, 2))
            status_values = list(ORDER_STATUSES.values())
            self._status_var = ctk.StringVar(value=status_values[0])
            self._status_menu = ctk.CTkOptionMenu(
                main_frame, variable=self._status_var, values=status_values, width=460
            )
            self._status_menu.pack(fill="x", pady=(0, 10))

        # --- Список напитков ---
        ctk.CTkLabel(main_frame, text="Выберите напитки:").pack(
            anchor="w", pady=(0, 5)
        )

        self._drinks_frame = ctk.CTkScrollableFrame(main_frame, height=300)
        self._drinks_frame.pack(fill="both", expand=True, pady=(0, 10))

        if not self._available_drinks:
            ctk.CTkLabel(
                self._drinks_frame, text="Нет доступных напитков", text_color="gray"
            ).pack(pady=20)
        else:
            for drink in self._available_drinks:
                var = ctk.BooleanVar(value=False)
                self._drink_vars[drink["id"]] = var

                label = (
                    f"{drink['name']} ({drink['category_name']}, {drink['size']})"
                    f" — {drink['price']} ₽"
                )
                ctk.CTkCheckBox(
                    self._drinks_frame, text=label, variable=var
                ).pack(anchor="w", pady=2)

        # --- Ошибка ---
        self._error_label = ctk.CTkLabel(
            main_frame, text="", text_color="red", wraplength=450
        )
        self._error_label.pack(fill="x", pady=(0, 10))

        # --- Кнопки ---
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(btn_frame, text="Сохранить", command=self._on_save_click).pack(
            side="left", expand=True, padx=(0, 5)
        )
        ctk.CTkButton(
            btn_frame, text="Отмена", fg_color="gray", command=self.destroy
        ).pack(side="left", expand=True, padx=(5, 0))

    def _fill_fields(self) -> None:
        if self._is_edit and hasattr(self, "_status_var"):
            status_display = ORDER_STATUSES.get(
                self._order_data.get("status", "new"), "Новый"
            )
            self._status_var.set(status_display)

        for drink_id in self._order_data.get("drink_ids", []):
            if drink_id in self._drink_vars:
                self._drink_vars[drink_id].set(True)

    def _on_save_click(self) -> None:
        self._error_label.configure(text="")

        selected_ids = [
            drink_id
            for drink_id, var in self._drink_vars.items()
            if var.get()
        ]

        if self._is_edit:
            status_key = "new"
            if hasattr(self, "_status_var"):
                status_display = self._status_var.get()
                for key, display in ORDER_STATUSES.items():
                    if display == status_display:
                        status_key = key
                        break

            order_id = self._order_data.get("id", "")
            success = self._on_save(order_id, selected_ids, status_key)
        else:
            success = self._on_save(selected_ids)

        if success:
            self.destroy()

    def show_error(self, message: str) -> None:
        self._error_label.configure(text=message)