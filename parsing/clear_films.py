import json
import os

# Указываем путь к файлу в папке "parsing"
films_file = os.path.join(os.path.dirname(__file__), "app/films.json")

# Проверяем, существует ли файл перед очисткой
if os.path.exists(films_file):
    with open(films_file, "w", encoding="utf-8") as file:
        json.dump([], file, ensure_ascii=False, indent=4)
    print("✅ Файл films.json очищен.")
else:
    print("⚠️ Файл films.json не найден. Очистка не требуется.")
#python -m parsing.clear_films  # Команда для запуска скрипта