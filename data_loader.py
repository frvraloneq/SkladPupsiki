import json
import os

DEFAULT_GROUPS = {
    "groups": {
        "Общие ответы": [
            {
                "name": "Приветствие",
                "text": "Здравствуйте! Сегодня {{date_full}} мы ожидаем доставку [дата доставки]."
            },
            {
                "name": "Номер накладной",
                "text": "Номер накладной: [номер накладной]"
            }
        ]
    }
}


def load_groups_from_file(scripts_file: str) -> dict:
    """Читает файл scripts.json и возвращает словарь групп."""
    if not os.path.exists(scripts_file):
        return {}

    with open(scripts_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("groups", {})


def create_example_groups_file(scripts_file: str) -> dict:
    """Создаёт примерный файл scripts.json, если его нет."""
    with open(scripts_file, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_GROUPS, f, ensure_ascii=False, indent=4)

    return DEFAULT_GROUPS["groups"]
