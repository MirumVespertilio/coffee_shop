import os

# Корневая директория проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Пути к файлам данных
DATA_DIR = os.path.join(BASE_DIR, "data")
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")
DRINKS_FILE = os.path.join(DATA_DIR, "drinks.json")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")

# Настройки окна
WINDOW_TITLE = "☕ CoffeeShop Manager"
WINDOW_SIZE = "1000x650"
WINDOW_MIN_SIZE = (800, 500)

# Тема customtkinter
APPEARANCE_MODE = "dark"
COLOR_THEME = "blue"

# Размеры напитков
DRINK_SIZES = ("S", "M", "L")

# Статусы заказов (ключ — значение для хранения, значение — отображение в UI)
ORDER_STATUSES = {
    "new": "Новый",
    "in_progress": "Готовится",
    "ready": "Готов",
    "cancelled": "Отменён",
}

# Предустановленные категории (используются при первом запуске)
DEFAULT_CATEGORIES = [
    "Кофе",
    "Чай",
    "Лимонад",
    "Смузи",
    "Горячий шоколад",
]

# Ограничения валидации
MAX_DRINK_NAME_LENGTH = 100
MAX_CATEGORY_NAME_LENGTH = 50
MAX_PRICE = 99999.99
MIN_PRICE = 0.01

# Текст для фильтров «без фильтра»
ALL_FILTER = "Все"