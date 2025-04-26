import time, sys, os
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.crud import (
    get_film_by_title, add_film, get_or_create_genre,
    get_or_create_actor, get_or_create_director
)
from app.database import SessionLocal

class FilmParser:
    def __init__(self, driver, db: Session):
        self.driver = driver
        self.db = db

    def scroll_and_click(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(element)).click()

    def get_film_links(self):
        url = "https://letterboxd.com/films/popular/page/4/"
        self.driver.get(url)
        time.sleep(5)
        print("✅ Страница с популярными фильмами загружена")

        movies = self.driver.find_elements(By.CSS_SELECTOR, "li.poster-container")[:72]
        films = []

        for movie in movies:
            title_elem = movie.find_element(By.CSS_SELECTOR, "img")
            title_raw = title_elem.get_attribute("alt")

            match = re.search(r'\((\d{4})\)', title_raw)
            year = int(match.group(1)) if match else "Unknown"
            title = re.sub(r'\s*\(\d{4}\)', '', title_raw).strip()
            poster = title_elem.get_attribute("src")

            link_elem = movie.find_element(By.CSS_SELECTOR, "a.frame")
            film_link = link_elem.get_attribute("href")
            full_link = f"https://letterboxd.com{film_link}" if film_link.startswith("/film/") else film_link

            films.append({"title": title, "year": year, "link": full_link, "poster": poster})

        print(f"✅ Найдено {len(films)} фильмов")
        return films

    def parse_film_page(self, film_url):
        print(f"🌐 Загружаем страницу: {film_url}")
        self.driver.get(film_url)
        wait = WebDriverWait(self.driver, 10)
        time.sleep(5)

        try:
            title_raw = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'meta[property="og:title"]'))).get_attribute("content")
            match = re.search(r'\((\d{4})\)', title_raw)
            year = int(match.group(1)) if match else "Unknown"
            title = re.sub(r'\s*\(\d{4}\)', '', title_raw).strip()

            description = self.driver.find_element(By.CSS_SELECTOR, 'meta[name="description"]').get_attribute("content")
            director_name = self.driver.find_element(By.CSS_SELECTOR, 'meta[name="twitter:data1"]').get_attribute("content")
            rating_text = self.driver.find_element(By.CSS_SELECTOR, 'meta[name="twitter:data2"]').get_attribute("content")
            poster = self.driver.find_element(By.CSS_SELECTOR, "meta[property='og:image']").get_attribute("content")

            try:
                rating = float(rating_text.split()[0])
            except ValueError:
                rating = None

            genres = self._parse_genres()
            actors = self._parse_actors()

            film = get_film_by_title(self.db, title)
            if not film:
                film = add_film(self.db, title, year, description, rating, poster)
                self.db.add(film)
                self.db.commit()
                self.db.refresh(film)

            self._associate_director(film, director_name)
            self._associate_genres(film, genres)
            self._associate_actors(film, actors)

            self.db.add(film)
            self.db.commit()
            self.db.refresh(film)

            return {
                "title": title,
                "year": year,
                "description": description,
                "director": director_name,
                "rating": rating,
                "poster": poster,
                "genres": genres,
                "actors": actors,
                "link": film_url
            }
        except Exception as e:
            print(f"❌ Ошибка при парсинге {film_url}: {e}")
            return None

    def _parse_genres(self):
        try:
            genres_tab = self.driver.find_element(By.CSS_SELECTOR, "a[data-id='genres']")
            self.scroll_and_click(genres_tab)
            time.sleep(3)
            genre_elements = self.driver.find_elements(By.CSS_SELECTOR, "#tab-genres .text-sluglist p a")
            return [g.text for g in genre_elements]
        except Exception as e:
            print(f"⚠️ Ошибка парсинга жанров: {e}")
            return []

    def _parse_actors(self):
        try:
            cast_tab = self.driver.find_element(By.CSS_SELECTOR, "a[data-id='cast']")
            self.scroll_and_click(cast_tab)
            time.sleep(3)
            show_all_button = self.driver.find_element(By.CSS_SELECTOR, "#show-cast-overflow")
            self.scroll_and_click(show_all_button)
            time.sleep(3)
            actor_elements = self.driver.find_elements(By.CSS_SELECTOR, "#tab-cast div p a")
            return [a.text for a in actor_elements]
        except Exception as e:
            print(f"⚠️ Ошибка парсинга актёров: {e}")
            return []

    def _associate_director(self, film, director_name):
        director = get_or_create_director(self.db, director_name)
        if director not in film.directors:
            film.directors.append(director)

    def _associate_genres(self, film, genres):
        for genre_name in genres:
            genre = get_or_create_genre(self.db, genre_name)
            if genre not in film.genres:
                film.genres.append(genre)

    def _associate_actors(self, film, actors):
        for actor_name in actors:
            actor = get_or_create_actor(self.db, actor_name)
            if actor not in film.actors:
                film.actors.append(actor)

def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    db = SessionLocal()

    try:
        parser = FilmParser(driver, db)
        films_links = parser.get_film_links()
        parsed_films = []

        for film in films_links:
            print(f"📥 Парсим: {film['title']}")
            film_info = parser.parse_film_page(film["link"])
            if film_info:
                parsed_films.append(film_info)

        print("✅ Парсинг завершён!")
    finally:
        driver.quit()
        db.close()


if __name__ == "__main__":
    main()
