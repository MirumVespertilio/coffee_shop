"""Функции валидации данных."""

from utils.constants import (
    MAX_DRINK_NAME_LENGTH,
    MAX_CATEGORY_NAME_LENGTH,
    MAX_PRICE,
    MIN_PRICE,
    DRINK_SIZES,
)


def validate_drink_name(name: str) -> str | None:
    """Валидация названия напитка. Возвращает текст ошибки или None."""
    if not name or not name.strip():
        return "Название не может быть пустым"
    if len(name.strip()) > MAX_DRINK_NAME_LENGTH:
        return f"Название слишком длинное (макс. {MAX_DRINK_NAME_LENGTH})"
    return None


def validate_drink_price(price_str: str) -> str | None:
    """Валидация цены напитка. Принимает строку из поля ввода."""
    if not price_str or not price_str.strip():
        return "Укажите цену"
    try:
        price = float(price_str.strip())
    except ValueError:
        return "Цена должна быть числом"

    if price < MIN_PRICE:
        return f"Цена должна быть не менее {MIN_PRICE}"
    if price > MAX_PRICE:
        return f"Цена не может превышать {MAX_PRICE}"
    return None


def validate_drink_size(size: str) -> str | None:
    """Валидация размера напитка."""
    if not size or size not in DRINK_SIZES:
        return "Выберите размер"
    return None


def validate_category_id(category_id: str | None) -> str | None:
    """Валидация выбора категории."""
    if not category_id:
        return "Выберите категорию"
    return None


def validate_category_name(name: str, existing_names: list[str]) -> str | None:
    """Валидация названия категории."""
    if not name or not name.strip():
        return "Название категории не может быть пустым"
    if len(name.strip()) > MAX_CATEGORY_NAME_LENGTH:
        return f"Название слишком длинное (макс. {MAX_CATEGORY_NAME_LENGTH})"
    # Проверка уникальности (регистронезависимо)
    if name.strip().lower() in [n.lower() for n in existing_names]:
        return "Такая категория уже существует"
    return None


def validate_order_drinks(drink_ids: list[str]) -> str | None:
    """Валидация списка напитков в заказе."""
    if not drink_ids:
        return "Добавьте хотя бы один напиток в заказ"
    return None