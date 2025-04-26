from app.celery_worker import celery_app  # Импортируем настройки Celery
from parsing.parse_films import FilmParser  # Импортируем твой парсер
from app.database import SessionLocal
from selenium import webdriver

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@celery_app.task
def parse_films_task():
    # Запускаем браузер
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    # Открываем базу данных
    db = SessionLocal()

    try:
        # Инстанцируем парсер
        parser = FilmParser(driver, db)
        films_links = parser.get_film_links()
        parsed_films = []

        # Запускаем парсинг
        for film in films_links:
            print(f"📥 Парсим: {film['title']}")
            film_info = parser.parse_film_page(film["link"])
            if film_info:
                parsed_films.append(film_info)

        print("✅ Парсинг завершён!")
    finally:
        driver.quit()
        db.close()
