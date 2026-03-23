"""Слой доступа к данным."""

from repository.interfaces import (
    ICategoryRepository,
    IDrinkRepository,
    IOrderRepository,
)
from repository.json_category_repository import JsonCategoryRepository
from repository.json_drink_repository import JsonDrinkRepository
from repository.json_order_repository import JsonOrderRepository